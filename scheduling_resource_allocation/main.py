from common.constants import DAG_FILE_PATH
from common.models import DirectedAcyclicGraph

if __name__ == "__main__":
    dag = DirectedAcyclicGraph.load_from_file(DAG_FILE_PATH)
    print(dag)
