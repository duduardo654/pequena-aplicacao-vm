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

case $opcao in
  1)
    echo ""
    read -p "Recriar o banco de Homologacao do zero (perde os dados)? [s/N]: " recriar_db
    echo "Derrubando Homologacao..."
    sudo docker compose stop app_homolog db_homolog
    sudo docker compose rm -f app_homolog db_homolog
    if [[ "$recriar_db" == "s" || "$recriar_db" == "S" ]]; then
      sudo docker volume rm pequena-aplicacao-vm_pgdata_homolog
    fi
    echo "Subindo Homologacao..."
    sudo docker compose up -d --build app_homolog db_homolog
    ;;
  2)
    echo ""
    read -p "Recriar o banco de Producao do zero (perde os dados)? [s/N]: " recriar_db
    echo "Derrubando Producao..."
    sudo docker compose stop app_prod db_prod
    sudo docker compose rm -f app_prod db_prod
    if [[ "$recriar_db" == "s" || "$recriar_db" == "S" ]]; then
      sudo docker volume rm pequena-aplicacao-vm_pgdata_prod
    fi
    echo "Subindo Producao..."
    sudo docker compose up -d --build app_prod db_prod
    ;;
  3)
    echo ""
    read -p "Recriar AMBOS os bancos do zero (perde os dados)? [s/N]: " recriar_db
    echo "Derrubando Homologacao e Producao..."
    sudo docker compose down
    if [[ "$recriar_db" == "s" || "$recriar_db" == "S" ]]; then
      sudo docker volume rm pequena-aplicacao-vm_pgdata_homolog pequena-aplicacao-vm_pgdata_prod
    fi
    echo "Subindo Homologacao e Producao..."
    sudo docker compose up -d --build
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
