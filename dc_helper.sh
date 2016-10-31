#!/bin/env bash
set -a

function enum_vars() {
  shopt -s nocasematch
  while IFS== read -r f1 f2 # f3 f4 f5 f6 f7
   do
      if [[ $f1 =~ \# ]]; then
        echo "skipping comment"
        continue
      elif [[ $f1 =~ docker ]]; then
        echo "found dc var"
        DOCKER_COMPOSE_ENV_VARS+=( $f1 )
      fi
      printf 'key: %s value: %s \n' "$f1" "$f2"
    done <"$1"
}

for i in "$@"; do
  if [[ -f "$i" ]]; then
    enum_vars "$i"
    echo "source $i"
    sudo source "$i"
  fi
done

for dckeys in "${DOCKER_COMPOSE_ENV_VARS[@]}"; do
    echo "${DOCKER_COMPOSE_ENV_VARS[*]}"
    echo " dc key is $dckeys ${!dckeys}"
    export $dckeys
done

sudo cat docker-compose.yml | envsubst | sudo -E docker-compose -f - up -d; RETV=$?
echo "$RETV"
sleep 1
echo 1
sleep 1
echo 2
sudo docker-compose ps
# sudo docker-compose logs
# sudo docker-compose ps
