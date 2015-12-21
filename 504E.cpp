#include <bits/stdc++.h>
using namespace std;

typedef unsigned long long ull;

const ull P = 127;
const ull Q = 480314964;
const ull R = 1000000007;

const int MAXN = 300007;
const int K = 19;

ull U[MAXN];
int clz[1 << K];

int N, M;
char S[MAXN];
vector<int> adj[MAXN];

int dep[MAXN];
int par[K][MAXN];
ull up[MAXN], dn[MAXN];

int far[MAXN], lc[MAXN];
int *id[MAXN], ch[MAXN];
int path[2 * MAXN], *ptr = path;

void dfs(int v, int p, int d){
  dep[v] = d;
  par[0][v] = p;
  up[v] = (P * up[p] + S[v]) % R;
  dn[v] = (Q * dn[p] + S[v]) % R;
  far[v] = 1;
  for(int n : adj[v]){
    if(n == p) continue;
    dfs(n, v, d + 1);
    if(far[n] + 1 > far[v]){
      lc[v] = n;
      far[v] = far[n] + 1;
    }
  }
  ch[lc[v]] = 1;
}

inline int jump(int a, int d){
  if(d == 0) return a;
  int k = clz[d];
  a = par[k][a];
  d ^= 1 << k;
  return id[a][-d];
}

inline int lca(int a, int b){
  if(dep[a] < dep[b]) swap(a, b);
  a = jump(a, dep[a] - dep[b]);
  if(a == b) return a;
  for(int i = K - 1; i >= 0; i--){
    if(par[i][a] != par[i][b]){
      a = par[i][a];
      b = par[i][b];
    }
  }
  return par[0][a];
}

inline ull get(int a, int b, int l, int k){
  if(k <= dep[a] - dep[l]){
    int v = jump(a, k);
    return (up[a] - U[k] * up[v] % R + R) % R;
  } else {
    int da = dep[a] - dep[l];
    int db = dep[b] - dep[l];
    int v = jump(b, da + db + 1 - k);
    int dv = dep[v] - dep[l];
    ull up_hash = (up[a] - U[da] * up[l] % R + R) % R;
    ull dn_hash = (U[dv] * dn[v] % R - dn[l] + R) % R;
    return (up_hash + U[da] * (S[l] + dn_hash)) % R;
  }
}

void init(){
  U[0] = 1;
  for(int i = 0; i < MAXN; i++){
    U[i + 1] = P * U[i] % R;
    clz[i] = 31 - __builtin_clz(i);
  }
}

void build(){
  scanf("%d%s", &N, S + 1);
  for(int i = 1; i < N; i++){
    int a, b;
    scanf("%d%d", &a, &b);
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  dep[0] = -1;
  dfs(1, 0, 0);
  for(int i = 0; i + 1 < K; i++){
    for(int j = 1; j <= N; j++){
      par[i + 1][j] = par[i][par[i][j]];
    }
  }
  for(int i = 1; i <= N; i++){
    if(!ch[i]){
      int u = par[0][i], v = i;
      int k = min(dep[i], far[i]);
      for(int j = 1; j <= k; j++){
        ptr[k - j] = u;
        u = par[0][u];
      }
      ptr += k;
      while(v > 0){
        id[v] = ptr;
        *ptr++ = v;
        v = lc[v];
      }
    }
  }
}

void solve(){
  scanf("%d", &M);
  for(int i = 0; i < M; i++){
    int a, b, c, d;
    scanf("%d%d%d%d", &a, &b, &c, &d);
    int l = lca(a, b), m = lca(c, d);
    int u = dep[a] + dep[b] - 2 * dep[l] + 1;
    int v = dep[c] + dep[d] - 2 * dep[m] + 1;
    int lo = 0, hi = min(u, v) + 1;
    while(lo + 1 < hi){
      int mid = (lo + hi) / 2;
      ull g = get(a, b, l, mid);
      ull h = get(c, d, m, mid);
      (g == h ? lo : hi) = mid;
    }
    printf("%d\n", lo);
  }
}

int main(){
  init();
  build();
  solve();
}
