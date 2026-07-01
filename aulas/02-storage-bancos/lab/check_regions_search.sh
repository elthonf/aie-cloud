regions="eastus eastus2 westus westus2 westus3 centralus northcentralus southcentralus brazilsouth canadacentral canadaeast uksouth ukwest westeurope northeurope francecentral germanywestcentral swedencentral norwayeast"

check_region() {
  region="$1"

  result=$(az search service list-skus \
    --location "$region" \
    -o tsv 2>/dev/null)

  if [ -n "$result" ]; then
    echo "Azure AI Search disponível: $region"
  else
    echo "Azure AI Search indisponível: $region"
  fi
}

export -f check_region

printf "%s\n" $regions | xargs -n 1 -P 6 bash -c 'check_region "$0"'