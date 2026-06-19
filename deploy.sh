#!/bin/bash

echo "=== Atualizando repositorio ==="
git pull

echo ""
echo "Qual ambiente deseja atualizar?"
echo "1) Homologacao (app_homolog + db_homolog)"
echo "2) Producao (app_prod + db_prod)"
echo "3) Ambos"
echo "4) Cancelar"
read -p "Escolha uma opcao [1-4]: " opcao

atualizar() {
  APP=$1
  DB=$2
  DB_NAME=$3
  VOLUME=$4

  echo ""
  echo "--- Backup de $DB_NAME (somente dados) ---"
  sudo docker exec -t "$DB" pg_dump -U postgres --data-only --column-inserts "$DB_NAME" > "backup_${DB_NAME}.sql"

  echo "--- Derrubando $APP e $DB (removendo volume para reler init.sql) ---"
  sudo docker compose stop "$APP" "$DB"
  sudo docker compose rm -f "$APP" "$DB"
  sudo docker volume rm "$VOLUME"

  echo "--- Subindo $APP e $DB com estrutura nova (init.sql roda automaticamente) ---"
  sudo docker compose up -d --build "$APP" "$DB"

  echo "--- Aguardando banco iniciar ---"
  sleep 8

  echo "--- Limpando dados de exemplo do init.sql ---"
  sudo docker exec -i "$DB" psql -U postgres -d "$DB_NAME" -c "TRUNCATE receita, usuario RESTART IDENTITY CASCADE;"

  echo "--- Restaurando dados reais de $DB_NAME ---"
  sudo docker exec -i "$DB" psql -U postgres -d "$DB_NAME" < "backup_${DB_NAME}.sql"

  echo "--- $DB_NAME atualizado com sucesso ---"
}

case $opcao in
  1)
    atualizar app_homolog db_homolog db_homolog pequena-aplicacao-vm_pgdata_homolog
    ;;
  2)
    atualizar app_prod db_prod db_prod pequena-aplicacao-vm_pgdata_prod
    ;;
  3)
    atualizar app_homolog db_homolog db_homolog pequena-aplicacao-vm_pgdata_homolog
    atualizar app_prod db_prod db_prod pequena-aplicacao-vm_pgdata_prod
    ;;
  4)
    echo "Operacao cancelada."
    exit 0
    ;;
  *)
    echo "Opcao invalida."
    exit 1
    ;;
esac

echo ""
echo "=== Status dos containers ==="
sudo docker compose ps