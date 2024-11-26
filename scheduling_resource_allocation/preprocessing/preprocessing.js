// Both chunks of text below were copied directly from the PDF
// This script transforms and combines them into a more usable format

const fs = require('fs');
const path = require('path');

const node_data_path = process.argv[2];
const matlab_incidence_mat_path = process.argv[3];
const dag_file_path = process.argv[4];

if (!node_data_path || !matlab_incidence_mat_path || !dag_file_path) {
  console.error("Usage: node script.js <node_data_path> <matlab_incidence_mat_path> <output_dag_file_path>");
  process.exit(1);
}

const node_data_text = fs.readFileSync(node_data_path, 'utf8')
const matlab_incidence_mat = fs.readFileSync(matlab_incidence_mat_path, 'utf8')

function skipComments(text) {
  return text.split("\n").filter(l => !l.trim().startsWith("//")).join("\n")
}

// -1 here since we use 0-based indexing but this uses 1-based indexing
const node_data = [...skipComments(node_data_text).matchAll(/(\d+) (\w+) (\d+) (\d+)/g)]
  .map(m => [parseInt(m[1]) - 1, m[2], parseInt(m[3]), parseInt(m[4])])

// -1 here since we use 0-based indexing but this uses 1-based indexing
const incidence_matrix = [...skipComments(matlab_incidence_mat).matchAll(/(\d+),(\d+)/g)]
  .map(m => m.slice(1, 3).map(d => parseInt(d) - 1))

const nodes = node_data.reduce((acc, curr) => {
  const idx = curr[0]
  acc[idx] = {
    "id": idx,
    "operation": curr[1],
    "due_date": curr[3]
  }
  return acc
}, {})

const operation_processing_time = node_data.reduce((acc, curr) => {
  acc[curr[1]] = curr[2]
  return acc
}, {})

const adjacency_matrix = incidence_matrix.reduce((acc, curr) => {
  if (!acc[curr[0]]) acc[curr[0]] = []
  if (!acc[curr[1]]) acc[curr[1]] = []
  acc[curr[0]].push(curr[1])
  return acc
}, {})

const reverse_adjacency_matrix = incidence_matrix.reduce((acc, curr) => {
  if (!acc[curr[0]]) acc[curr[0]] = []
  if (!acc[curr[1]]) acc[curr[1]] = []
  acc[curr[1]].push(curr[0])
  return acc
}, {})

const node_out_degrees = Object.entries(adjacency_matrix).reduce((acc, [n, children]) => {
  acc[n] = children.length
  return acc
}, {})

const node_in_degrees = Object.entries(reverse_adjacency_matrix).reduce((acc, [n, parents]) => {
  acc[n] = parents.length
  return acc
}, {})

const directed_acyclic_graph = {
  nodes,
  operation_processing_time,
  adjacency_matrix,
  reverse_adjacency_matrix,
  node_in_degrees,
  node_out_degrees
}

const dag_dir = path.dirname(dag_file_path);
fs.mkdirSync(dag_dir, { recursive: true });

fs.writeFileSync(dag_file_path, JSON.stringify(directed_acyclic_graph, null, 2))
