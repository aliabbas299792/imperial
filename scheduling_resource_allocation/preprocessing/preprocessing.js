// Both chunks of text below were copied directly from the PDF
// This script transforms and combines them into a more usable format

const fs = require('fs'); 

const dag_file_name = "artefacts/directed_acyclic_graph.json"

const node_data_text = `1 onnx 3 172 17 wave 6 233
2 muse 10 82 18 wave 6 77
3 emboss 2 18 19 emboss 2 88
4 emboss 2 61 20 onnx 3 122
5 blur 5 93 21 emboss 2 71
6 emboss 2 71 22 onnx 3 181
7 vii 14 217 23 vii 14 340
8 blur 5 295 24 blur 5 141
9 wave 6 290 25 night 18 209
10 blur 5 287 26 muse 10 217
11 blur 5 253 27 emboss 2 256
12 emboss 2 307 28 onnx 3 144
13 onnx 3 279 29 wave 6 307
14 onnx 3 73 30 emboss 2 329
15 blur 5 355 31 muse 10 269
16 wave 6 34`

const incidence_matrix_text = `G[0, 30]=1;
G[1, 0]=1;
G[2, 7]=1;
G[3, 2]=1;
G[4, 1]=1;
G[5, 15]=1;
G[6, 5]=1;
G[7, 6]=1;
G[8, 7]=1;
G[9, 8]=1;
G[10, 0]=1;
G[11, 4]=1;
G[12, 11]=1;
G[13, 12]=1;
G[16, 14]=1;
G[14, 10]=1;
G[15, 4]=1;
G[16, 15]=1;
G[17, 16]=1;
G[18, 17]=1;
G[19, 18]=1;
G[20, 17]=1;
G[21, 20]=1;
G[22, 21]=1;
G[23, 4]=1;
G[24, 23]=1;
G[25, 24]=1;
G[26, 25]=1;
G[27, 25]=1;
G[28, 26]=1;
G[28, 27]=1;
G[29, 3]=1;
G[29, 9]=1;
G[29, 13]=1;
G[29, 19]=1;
G[29, 22]=1;
G[29, 28]=1;`

const node_data = [...node_data_text.matchAll(/(\d+) (\w+) (\d+) (\d+)/g)]
    .map(m => [parseInt(m[1]), m[2], parseInt(m[3]), parseInt(m[4])])

const incidence_matrix = [...incidence_matrix_text.matchAll(/(\d+), (\d+)/g)]
    .map(m => m.slice(1,3).map(d => parseInt(d)))

const nodes = node_data.reduce((acc, curr) => {
    const idx = curr[0] - 1
    acc[idx] = {
        "id": idx,
        "operation": curr[1],
        "due_date": curr[3]
    }
    return acc
}, new Array(node_data.length))

const operation_processing_time = node_data.reduce((acc, curr) => {
    acc[curr[1]] = curr[2]
    return acc
}, {})

const adjacency_graph = incidence_matrix.reduce((acc, curr) => {
    if(!acc[curr[0]]) acc[curr[0]] = []
    if(!acc[curr[1]]) acc[curr[1]] = []
    acc[curr[0]].push(curr[1])
    return acc
}, {})

const directed_acyclic_graph = {
    nodes,
    operation_processing_time,
    adjacency_graph
}

fs.writeFileSync(dag_file_name, JSON.stringify(directed_acyclic_graph, null, 2))
