alias ll='ls -al'

eval $(docker-machine env default)

# alias rsync='docker run --rm -v ~/tpam:/data drsync_image rsync'

docker () {
  MSYS_NO_PATHCONV=1 docker.exe $@
}
export -f docker

export HTTP_PROXY=http://proxy.dcl.example.com:8080
export http_proxy=http://proxy.dcl.example.com:8080

export HTTPS_PROXY=http://proxy.dcl.example.com:8080
export https_proxy=http://proxy.dcl.example.com:8080

export no_proxy=192.168.99.100,localhost,127.0.0.1

export PATH=/c/Anaconda3/envs/tpam/Scripts/:$PATH
