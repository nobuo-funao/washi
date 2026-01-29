import streamlit as st

def lsb_bit(x: int) -> int:
  return x & -x

def bit_to_digit(bit: int) -> int:
  return (bit.bit_length() - 1) + 1

def digit_to_bit(d: int) -> int:
  return 1 << (d - 1)

ALL  = (1 << 9) - 1  # 9 bits
ROWS = [[r * 9 + c for c in range(9)] for r in range(9)]
COLS = [[r * 9 + c for r in range(9)] for c in range(9)]
BOXS = []
for br in range(3):
  for bc in range(3):
    unit = []
    for r in range(br * 3, br * 3 + 3):
      for c in range(bc * 3, bc * 3 + 3):
        unit.append(r * 9 + c)
    BOXS.append(unit)

UNITS      = ROWS + COLS + BOXS
CELL_UNITS = [[] for _ in range(81)]
for ui, u in enumerate(UNITS):
  for idx in u:
    CELL_UNITS[idx].append(ui)

PEERS = [None] * 81
for idx in range(81):
  s = set()
  for ui in CELL_UNITS[idx]:
    s.update(UNITS[ui])
  s.discard(idx)
  PEERS[idx] = tuple(s)

def is_single(m: int) -> bool:
  return (m & (m - 1)) == 0

def bitcount(x: int) -> int:
  return x.bit_count()

class Contradiction(Exception):
  pass

def record_set(cand, i, new_mask, trail):
  old = cand[i]
  if old == new_mask:
    return
  if new_mask == 0:
    raise Contradiction
  cand[i] = new_mask
  trail.append((i, old))

def eliminate(cand, idx, bit, trail):
  m = cand[idx]
  if (m & bit) == 0:
    return
  new_m = m & ~bit
  record_set(cand, idx, new_m, trail)

  if is_single(new_m):
    b = new_m
    for p in PEERS[idx]:
      eliminate(cand, p, b, trail)

  for ui in CELL_UNITS[idx]:
    places = 0
    last = -1
    for j in UNITS[ui]:
      if cand[j] & bit:
        places += 1
        last = j
        if places >= 2:
          break
    if places == 0:
      raise Contradiction
    if places == 1:
      assign(cand, last, bit_to_digit(bit), trail)

def assign(cand, idx, d, trail):
  bit = digit_to_bit(d)
  m = cand[idx]
  if m == bit:
    return
  if (m & bit) == 0:
    raise Contradiction
  other = m & ~bit
  while other:
    b = lsb_bit(other)
    other ^= b
    eliminate(cand, idx, b, trail)

def select_mrv(cand):
  best_i = -1
  best_k = 10
  for i, m in enumerate(cand):
    if is_single(m):
      continue
    k = bitcount(m)
    if k < best_k:
      best_k = k
      best_i = i
      if k == 2:
        break
  return best_i

def solved(cand):
  return all(is_single(m) for m in cand)

def search(cand):
  if solved(cand):
    return True
  i = select_mrv(cand)
  m = cand[i]

  mm = m
  while mm:
    b = lsb_bit(mm)
    mm ^= b

    trail = []
    try:
      assign(cand, i, bit_to_digit(b), trail)
      if search(cand):
        return True
    except Contradiction:
      pass

    for j, old in reversed(trail):
      cand[j] = old

  return False

def solve_grid(grid81: str):
  if len(grid81) != 81:
    raise ValueError("盤面は81文字で指定してください。")
  cand = [ALL] * 81
  trail = []
  try:
    for i, ch in enumerate(grid81):
      if ch in "0.":
        continue
      if ch < "1" or ch > "9":
        raise ValueError("数字は1-9、空マスは0または.で入力してください。")
      assign(cand, i, int(ch), trail)
  except Contradiction:
    return None

  if not search(cand):
    return None

  return "".join(str(bit_to_digit(m)) for m in cand)

def pretty(grid81: str) -> str:
  s = grid81
  lines = []
  for r in range(9):
    row = []
    for c in range(9):
      ch = s[r * 9 + c]
      row.append(ch if ch not in "0." else ".")
      if c in (2, 5):
        row.append("|")
    lines.append(" ".join(row))
    if r in (2, 5):
      lines.append("-" * 21)
  return "\n".join(lines)

# Streamlit UI (data_editor)
st.set_page_config(page_title="Sudoku Solver", layout="centered")
st.title("数独（ナンプレ）ソルバー")
st.caption("表をクリックして 1 ～ 9 を入力（空欄は空のまま）→「解く」")

SAMPLE = (
  "000000070"
  "060010004"
  "003400200"
  "800003050"
  "002900700"
  "040080009"
  "020060007"
  "000100900"
  "700008060"
)

def grid81_to_rows(grid81: str):
  rows = []
  for r in range(9):
    row = []
    for c in range(9):
      ch = grid81[r * 9 + c]
      row.append("" if ch in "0." else ch)  # keep as str
    rows.append(row)
  return rows

def rows_to_grid81(rows):
  # rows: list[list[Any]] 9x9
  out = []
  for r in range(9):
    for c in range(9):
      v = rows[r][c]
      if v is None:
        out.append("0")
        continue
      s = str(v).strip()
      if s == "":
        out.append("0")
      elif s in "123456789":
        out.append(s)
      else:
        # invalid -> treat as empty (and show warning later)
        out.append("0")
  return "".join(out)

if "rows" not in st.session_state:
  st.session_state.rows = grid81_to_rows("0" * 81)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
  if st.button("クリア", use_container_width=True):
    st.session_state.rows = grid81_to_rows("0" * 81)
with col2:
  if st.button("サンプルを入れる", use_container_width=True):
    st.session_state.rows = grid81_to_rows(SAMPLE)
with col3:
  show_raw = st.toggle("81文字", value=False)

st.write("### 入力（9x9）")

edited = st.data_editor(
  st.session_state.rows,
  num_rows="fixed",
  use_container_width=True,
  key="sudoku_editor",
)

grid81 = rows_to_grid81(edited)

# 入力チェック（不正文字が混じっていたら警告）
invalid_found = False
for r in range(9):
  for c in range(9):
    v = edited[r][c]
    if v is None or str(v).strip() == "":
      continue
    s = str(v).strip()
    if s not in "123456789":
      invalid_found = True
      break
  if invalid_found:
    break

if invalid_found:
  st.warning("1～9以外が入力されています。空欄にするか、1～9にしてください。")

if show_raw:
  st.code(grid81)

if st.button("解く", type="primary", use_container_width=True):
  ans = solve_grid(grid81)
  if ans is None:
    st.error("解けませんでした（矛盾、または解なし）。")
    st.text(pretty(grid81))
  else:
    st.text(pretty(ans))
    st.session_state.rows = grid81_to_rows(ans)
    st.rerun()

st.caption("実行: `pip install streamlit` の後、`streamlit run sudoku.py`")
st.markdown('【参考】エクストリームナンプレ: `https://sudoku.com/jp/extreme/`')
