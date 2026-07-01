echo "Verificando regions com SQL Server para sua conta ..."

regions="eastus eastus2 westus westus2 westus3 centralus northcentralus southcentralus brazilsouth canadacentral canadaeast uksouth ukwest westeurope northeurope francecentral germanywestcentral swedencentral norwayeast"

check_region() {
  region="$1"

  result=$(az sql list-usages \
    --location "$region" \
    -o tsv 2>/dev/null)

  if [ -n "$result" ]; then
    echo "SQL Database disponível: $region"
  else
    echo "SQL Database indisponível: $region"
  fi
}

export -f check_region

printf "%s\n" $regions | xargs -n 1 -P 6 bash -c 'check_region "$0"'