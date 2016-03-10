alias ll='ls -al'

eval $(docker-machine env default)

docker () {
  MSYS_NO_PATHCONV=1 docker.exe $@
}
export -f docker

export PATH=/c/miniconda/envs/dstack/Scripts/:$PATH
