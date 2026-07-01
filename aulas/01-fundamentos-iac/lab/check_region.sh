echo "Verificando regions com VM para sua conta ..."

regions="eastus eastus2 westus westus2 westus3 centralus northcentralus southcentralus brazilsouth canadacentral canadaeast uksouth ukwest westeurope northeurope francecentral germanywestcentral swedencentral norwayeast"

check_region() {
  region="$1"

  result=$(az vm list-skus \
    --location "$region" \
    --size Standard_D2s_v3 \
    --query "[?restrictions[?type=='Location']].restrictions" \
    -o tsv 2>/dev/null)

  if [ -z "$result" ]; then
    echo "VM Standard_D2s_v3 disponível: $region"
  else
    echo "VM Standard_D2s_v3 indisponível: $region"
  fi
}

export -f check_region

printf "%s\n" $regions | xargs -n 1 -P 6 bash -c 'check_region "$0"'