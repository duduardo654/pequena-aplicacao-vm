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

  echo ""
  echo "--- Backup de $DB_NAME ---"
  sudo docker exec -t "$DB" pg_dump -U postgres "$DB_NAME" > "backup_${DB_NAME}.sql"

  echo "--- Derrubando $APP e $DB ---"
  sudo docker compose stop "$APP" "$DB"
  sudo docker compose rm -f "$APP" "$DB"

  echo "--- Subindo $APP e $DB com estrutura nova ---"
  sudo docker compose up -d --build "$APP" "$DB"

  echo "--- Aguardando banco iniciar ---"
  sleep 8

  echo "--- Restaurando dados em $DB_NAME ---"
  sudo docker exec -i "$DB" psql -U postgres -d "$DB_NAME" < "backup_${DB_NAME}.sql"

  echo "--- $DB_NAME atualizado com sucesso ---"
}

case $opcao in
  1)
    atualizar app_homolog db_homolog db_homolog
    ;;
  2)
    atualizar app_prod db_prod db_prod
    ;;
  3)
    atualizar app_homolog db_homolog db_homolog
    atualizar app_prod db_prod db_prod
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