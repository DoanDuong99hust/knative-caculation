from lib2to3.pgen2.token import COLON, SLASH


# HOST IP
MASTER_HOST = "localhost"
MASTER_USERNAME = "core"
MASTER_PASSWORD = "1"
PI_IP = "192.168.101.217"

CALCULATING_HOSTNAME = "node1"
CALCULATING_INSTANCE = "192.168.101.154"

# PORT
PROMETHEUS_PORT = "8080"

COLON = ":"
SLASH = "/"
TEST_MODE = False

PROMETHEUS_DOMAIN = "http://"+ MASTER_HOST + COLON + PROMETHEUS_PORT +"/api/v1/query?query="
SERVICE_DOMAIN = "http://detection.default.svc.cluster.local"

# QUERY
VALUES_CPU_QUERY = "100-(avg%20by%20(instance,job)(irate(node_cpu_seconds_total{mode='idle',job='node_exporter',instance='"+CALCULATING_INSTANCE+":9100'}[30s])*100))"
VALUES_PODS_QUERY = "kubelet_running_pods{kubernetes_io_hostname='"+CALCULATING_HOSTNAME+"'}"
VALUES_MEMORY_QUERY = "(node_memory_MemTotal_bytes{job='node_exporter',instance='"+CALCULATING_INSTANCE+":9100'}-node_memory_MemAvailable_bytes{job='node_exporter',instance='"+CALCULATING_INSTANCE+":9100'})/(1024*1024)"
RUNNING_PODS_QUERY = "kubelet_running_pods{kubernetes_io_hostname='"+CALCULATING_HOSTNAME+"'}"
POD_STATUS_PHASE_QUERY = "kube_pod_status_phase{namespace='capture',job='Kubernetes'}"

# FOLDER
SERVER_FOLDER = "server"

# FILE NAME
POD_START_TIME_FILENAME = "pod_start_time_{}_{}.csv"
DATA_PROMETHEUS_AT_SERVER_FILENAME = "data-prometheus_{}_{}_server.csv"
TIMESTAMP_FILENAME = "timestamps_{}_{}_server.csv"

# DIRECTORIES
DATA_DIRECTORY = "/home/core/DoanDuong/knative-caculation/data/"
POD_START_TIME_DATA_FILE_DIRECTOR = DATA_DIRECTORY + POD_START_TIME_FILENAME
DATA_PROMETHEUS_AT_SERVER_FILE_DIRECTORY = DATA_DIRECTORY + SERVER_FOLDER + SLASH + DATA_PROMETHEUS_AT_SERVER_FILENAME
TIMESTAMP_DATA_FILE_DIRECTORY = DATA_DIRECTORY + SERVER_FOLDER + SLASH + TIMESTAMP_FILENAME


# COMMAND
START_UMMETER_CMD = '/usr/bin/python3 /home/core/DoanDuong/knative-caculation/usbmeter --addr 00:16:A5:00:0F:65 --out /home/luongtrann/hanoi/code/data_ummeter/data_ummeter_{}_{} --time {}'
UPDATE_REPLICAS_CMD = '/usr/bin/python3 /home/core/DoanDuong/knative-caculation/main.py changevalue {} {} {}'

# STATUS
COLD_START_STATUS = "cold_start"
COLD_DONE_STATUS = "cold_done"
COLD_END_STATUS = "cold_end"
WARM_START_STATUS = "warm_start"
WARM_DONE_STATUS = "warm_done"
WARM_END_STATUS = "warm_end"
DELETE_START_STATUS = "delete_start"
DELETE_DONE_STATUS = "delete_done"
POD_DELETE_AFTER_STATUS = "pods_deleted_after"
PENDING_STATUS = "Pending"
RUNNING_STATUS = "Running"

COLD_PROCESSING = "cold_processing"
COLD_TO_WARM_PROCESSING = "cold_to_warm_processing"
WARM_PROCESSING = "warm_processing"
ACTIVE_PROCESSING = "active_processing"
DELETE_PROCESSING = "delete_processing"

COLD_JOB = "cold"
COLD_TO_WARM = "cold_to_warm"
WARM_JOB = "warm"
ACTIVE_JOB = "active"
DELETE_JOB = "delete"
