#include <iostream>
#include <vector>
#include <queue>

using namespace std;

const int MAX_M = 7;
const int MAX_N = 7;

struct Cell {
  int row;
  int col;
  int data;

  bool operator<(const Cell& other) const {
    return data < other.data;
  }
};

int findMinData(vector<vector<int>>& warehouse, Cell virusPos, Cell dummyPos) {
  int m = warehouse.size();
  int n = warehouse[0].size();

  // Initialize visited array
  vector<vector<bool>> visited(m, vector<bool>(n, false));

  // Priority queue to store cells based on data
  priority_queue<Cell> pq;
  pq.push(virusPos);

  int totalData = 0;

  while (!pq.empty()) {
    Cell current = pq.top();
    pq.pop();

    if (visited[current.row][current.col]) {
      continue;
    }

    visited[current.row][current.col] = true;

    // Check if we reached the dummy container
    if (current.row == dummyPos.row && current.col == dummyPos.col) {
      return totalData;
    }

    // Process neighbors
    for (int i = -1; i <= 1; ++i) {
      for (int j = -1; j <= 1; ++j) {
        int newRow = current.row + i;
        int newCol = current.col + j;

        if (0 <= newRow && newRow < m && 0 <= newCol && newCol < n && !visited[newRow][newCol]) {
          // Check if data needs to be fudged
          if (warehouse[newRow][newCol] < current.data) {
            warehouse[newRow][newCol] = current.data;
            totalData += (current.data - warehouse[newRow][newCol]);
          }

          pq.push({newRow, newCol, warehouse[newRow][newCol]});
        }
      }
    }
  }

  return -1; // Cannot reach the dummy container
}

int main() {
  int m, n;
  cin >> m >> n;

  // Read warehouse data
  vector<vector<int>> warehouse(m, vector<int>(n));
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j < n; ++j) {
      cin >> warehouse[i][j];
    }
  }

  // Read virus and dummy container positions
  Cell virusPos, dummyPos;
  cin >> virusPos.row >> virusPos.col;
  cin >> dummyPos.row >> dummyPos.col;

  // Calculate and print minimum data required
  int minData = findMinData(warehouse, virusPos, dummyPos);
  if (minData == -1) {
    cout << "Destination unreachable";
  } else {
    cout << minData;
  }

  return 0;
}