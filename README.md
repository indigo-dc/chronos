# chronos
Dockerfile to build Chronos docker image

Chronos https://mesos.github.io/chronos/

<pre>
docker run -d \
-e CHRONOS_HTTP_PORT=4400 \
-e CHRONOS_MASTER=zk://$node-1:2181,$node-2:2181,$node-3:2181/mesos \
-e CHRONOS_ZK_HOSTS=zk://$node-1:2181,$node-2:2181,$node-3:2181 \
-e CHRONOS_HOSTNAME=$ip \
-e CHRONOS_MESOS_FRAMEWORK_NAME=$name \
-e CHRONOS_ZK_PATH=$zkpath \ 
--name chronos --net host --restart always indigodatacloud/chronos
</pre>

