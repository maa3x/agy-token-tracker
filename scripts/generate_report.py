#!/usr/bin/env python3
import os
import sys
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from get_tokens import get_all_conversations, get_conversation_details

def generate_html_report(all_data, output_path):
    # Collect detailed turns for the top 50 conversations for interactive modal inside artifact
    detailed_data = []
    for item in all_data[:50]:
        details = get_conversation_details(item["conversation_id"])
        if details:
            detailed_data.append(details)
        else:
            detailed_data.append(item)
    
    # If more than 50, append the rest with basic summary
    if len(all_data) > 50:
        detailed_data.extend(all_data[50:])

    json_data = json.dumps(detailed_data)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>All Conversations Token Report</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --background: #0f172a;
      --card: #1e293b;
      --card-hover: #334155;
      --border: #334155;
      --foreground: #f8fafc;
      --muted-foreground: #94a3b8;
      --primary: #38bdf8;
      --primary-foreground: #0f172a;
      --accent: #818cf8;
      --success: #34d399;
    }}
    body {{
      background-color: transparent;
      color: var(--foreground);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    th.sortable {{
      cursor: pointer;
      user-select: none;
    }}
    th.sortable:hover {{
      color: var(--primary);
    }}
    tr.clickable-row {{
      cursor: pointer;
    }}
  </style>
</head>
<body class="p-2 sm:p-4">
  <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl p-5 shadow-sm space-y-6 max-w-5xl mx-auto">

    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border)] pb-4">
      <div>
        <h2 class="text-xl font-bold tracking-tight text-[var(--foreground)] flex items-center gap-2">
          <span>⚡</span> گزارش مصرف توکن تمام گفتگوها
        </h2>
        <p class="text-xs text-[var(--muted-foreground)] mt-0.5">
          برای مشاهده ریز مراحل هر گفتگو، روی آن کلیک کنید.
        </p>
      </div>
      <div id="countBadge" class="text-xs text-[var(--muted-foreground)] bg-[var(--background)] px-3 py-1.5 rounded-lg border border-[var(--border)]">
        بارگذاری...
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-[var(--background)]/60 border border-[var(--border)] rounded-xl p-3.5">
        <span class="text-[11px] font-medium text-[var(--muted-foreground)] uppercase">مجموع توکن</span>
        <div id="statTotal" class="text-xl font-bold text-[var(--primary)] font-mono mt-1">-</div>
      </div>
      <div class="bg-[var(--background)]/60 border border-[var(--border)] rounded-xl p-3.5">
        <span class="text-[11px] font-medium text-[var(--muted-foreground)] uppercase">ورودی (Input)</span>
        <div id="statInput" class="text-xl font-bold text-[var(--foreground)] font-mono mt-1">-</div>
      </div>
      <div class="bg-[var(--background)]/60 border border-[var(--border)] rounded-xl p-3.5">
        <span class="text-[11px] font-medium text-[var(--muted-foreground)] uppercase">خروجی (Output)</span>
        <div id="statOutput" class="text-xl font-bold text-[var(--foreground)] font-mono mt-1">-</div>
      </div>
      <div class="bg-[var(--background)]/60 border border-[var(--border)] rounded-xl p-3.5">
        <span class="text-[11px] font-medium text-[var(--muted-foreground)] uppercase">خوانده از کش</span>
        <div id="statCache" class="text-xl font-bold text-[var(--success)] font-mono mt-1">-</div>
      </div>
    </div>

    <!-- Visual Chart: Top Conversations -->
    <div class="bg-[var(--background)]/40 border border-[var(--border)] rounded-xl p-4 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)] flex items-center gap-1.5">
          <span>📊</span> بیشترین مصرف توکن (Top 7 Conversations)
        </h3>
        <span class="text-[11px] text-[var(--muted-foreground)]">کلیک برای مشاهده جزئیات</span>
      </div>
      <div id="chartContainer" class="space-y-2 pt-1"></div>
    </div>

    <!-- Filter & Search -->
    <div class="relative">
      <input type="text" id="searchInput" placeholder="جستجو بر اساس عنوان یا شناسه گفتگو..."
             class="w-full bg-[var(--background)]/70 border border-[var(--border)] rounded-xl px-3.5 py-2.5 text-xs text-[var(--foreground)] placeholder-[var(--muted-foreground)] focus:outline-none focus:border-[var(--primary)]">
    </div>

    <!-- Sortable Table -->
    <div class="border border-[var(--border)] rounded-xl overflow-hidden bg-[var(--background)]/30">
      <div class="overflow-x-auto max-h-96">
        <table class="w-full text-left text-xs">
          <thead class="bg-[var(--card)] sticky top-0 border-b border-[var(--border)] text-[11px] text-[var(--muted-foreground)] uppercase">
            <tr>
              <th class="py-2.5 px-3 sortable" data-col="title">
                عنوان و شناسه گفتگو <span id="sort_title"></span>
              </th>
              <th class="py-2.5 px-2 text-center sortable" data-col="turn_count">
                دورها <span id="sort_turn_count"></span>
              </th>
              <th class="py-2.5 px-2 text-right sortable" data-col="input_tokens">
                ورودی <span id="sort_input_tokens"></span>
              </th>
              <th class="py-2.5 px-2 text-right sortable" data-col="output_tokens">
                خروجی <span id="sort_output_tokens"></span>
              </th>
              <th class="py-2.5 px-2 text-right sortable" data-col="total_tokens">
                مجموع <span id="sort_total_tokens">▼</span>
              </th>
              <th class="py-2.5 px-2 text-right sortable" data-col="cache_read_tokens">
                کش <span id="sort_cache_read_tokens"></span>
              </th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-[var(--border)]/60"></tbody>
        </table>
      </div>
    </div>

  </div>

  <!-- Detail Modal -->
  <div id="detailModal" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-6 hidden">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <div class="p-4 border-b border-[var(--border)] flex items-start justify-between gap-3 bg-[var(--card)]">
        <div class="space-y-1 max-w-xl">
          <h3 id="modalTitle" class="text-sm sm:text-base font-bold text-[var(--foreground)] truncate"></h3>
          <div class="flex items-center gap-2 text-[11px] text-[var(--muted-foreground)]">
            <span class="font-mono bg-[var(--background)] px-1.5 py-0.5 rounded border border-[var(--border)]" id="modalCid"></span>
            <span id="modalTime"></span>
          </div>
        </div>
        <button id="closeModalBtn" class="text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-2xl font-light p-1">
          &times;
        </button>
      </div>

      <div class="p-4 overflow-y-auto space-y-4">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-2.5">
            <span class="text-[10px] text-[var(--muted-foreground)] uppercase">مجموع توکن</span>
            <div id="modalTotal" class="text-base font-bold text-[var(--primary)] font-mono mt-0.5">-</div>
          </div>
          <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-2.5">
            <span class="text-[10px] text-[var(--muted-foreground)] uppercase">ورودی</span>
            <div id="modalInput" class="text-base font-bold text-[var(--foreground)] font-mono mt-0.5">-</div>
          </div>
          <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-2.5">
            <span class="text-[10px] text-[var(--muted-foreground)] uppercase">خروجی</span>
            <div id="modalOutput" class="text-base font-bold text-[var(--foreground)] font-mono mt-0.5">-</div>
          </div>
          <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-2.5">
            <span class="text-[10px] text-[var(--muted-foreground)] uppercase">کش شده</span>
            <div id="modalCache" class="text-base font-bold text-[var(--success)] font-mono mt-0.5">-</div>
          </div>
        </div>

        <div id="modalPromptContainer" class="bg-[var(--background)]/60 border border-[var(--border)] rounded-xl p-3 space-y-1">
          <span class="text-[10px] font-medium text-[var(--muted-foreground)] uppercase">درخواست اولیه</span>
          <p id="modalPromptText" class="text-xs text-[var(--foreground)] line-clamp-3 select-text"></p>
        </div>

        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold uppercase text-[var(--muted-foreground)]">ریز مصرف مراحل</span>
            <span id="modalTurnBadge" class="text-[11px] text-[var(--muted-foreground)]"></span>
          </div>

          <div class="border border-[var(--border)] rounded-xl overflow-hidden bg-[var(--background)]/40">
            <div class="overflow-x-auto max-h-56">
              <table class="w-full text-left text-[11px]">
                <thead class="bg-[var(--card)] sticky top-0 border-b border-[var(--border)] text-[10px] text-[var(--muted-foreground)] uppercase">
                  <tr>
                    <th class="py-2 px-2.5 text-center">دور</th>
                    <th class="py-2 px-2.5">ابزارها</th>
                    <th class="py-2 px-2.5 text-right">ورودی</th>
                    <th class="py-2 px-2.5 text-right">خروجی</th>
                    <th class="py-2 px-2.5 text-right">مجموع</th>
                    <th class="py-2 px-2.5 text-right">کش</th>
                  </tr>
                </thead>
                <tbody id="modalTurnsBody" class="divide-y divide-[var(--border)]/50"></tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>

  <script>
    const allData = {json_data};
    let sortCol = 'total_tokens';
    let sortAsc = false;
    const fmt = n => (n || 0).toLocaleString();

    function showDetails(cid) {{
      const item = allData.find(x => x.conversation_id === cid);
      if (!item) return;

      document.getElementById('modalTitle').textContent = item.title || 'گفتگو';
      document.getElementById('modalCid').textContent = item.conversation_id;
      document.getElementById('modalPromptText').textContent = item.full_prompt || item.first_prompt || '(بدون متن)';
      document.getElementById('modalTotal').textContent = fmt(item.total_tokens);
      document.getElementById('modalInput').textContent = fmt(item.input_tokens);
      document.getElementById('modalOutput').textContent = fmt(item.output_tokens);
      document.getElementById('modalCache').textContent = fmt(item.cache_read_tokens);
      document.getElementById('modalTurnBadge').textContent = `${{item.turn_count}} دور`;

      if (item.start_time) {{
        const d = new Date(item.start_time);
        document.getElementById('modalTime').textContent = `📅 ${{d.toLocaleDateString()}} ${{d.toLocaleTimeString()}}`;
      }} else {{
        document.getElementById('modalTime').textContent = '';
      }}

      const turnsBody = document.getElementById('modalTurnsBody');
      if (!item.turns || item.turns.length === 0) {{
        turnsBody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-xs text-[var(--muted-foreground)]">ریز مراحل موجود نیست</td></tr>';
      }} else {{
        turnsBody.innerHTML = item.turns.map((t, idx) => {{
          const tools = t.tools && t.tools.length > 0
            ? t.tools.map(x => `<span class="inline-block px-1 py-0.5 rounded text-[9px] bg-sky-500/10 text-sky-400 border border-sky-500/20 mr-1">${{x}}</span>`).join('')
            : '<span class="text-[10px] text-[var(--muted-foreground)]">پاسخ مستقیم</span>';

          return `
            <tr class="hover:bg-[var(--card-hover)]">
              <td class="py-1.5 px-2.5 text-center font-mono text-[var(--muted-foreground)]">${{idx + 1}}</td>
              <td class="py-1.5 px-2.5">${{tools}}</td>
              <td class="py-1.5 px-2.5 text-right font-mono text-[var(--foreground)]">${{fmt(t.input)}}</td>
              <td class="py-1.5 px-2.5 text-right font-mono text-[var(--foreground)]">${{fmt(t.output)}}</td>
              <td class="py-1.5 px-2.5 text-right font-mono font-semibold text-[var(--primary)]">${{fmt(t.total)}}</td>
              <td class="py-1.5 px-2.5 text-right font-mono text-[var(--success)]">${{fmt(t.cache)}}</td>
            </tr>
          `;
        }}).join('');
      }}

      document.getElementById('detailModal').classList.remove('hidden');
    }}

    function renderChart(data) {{
      const topItems = [...data].sort((a,b) => b.total_tokens - a.total_tokens).slice(0, 7);
      const maxVal = topItems.length > 0 ? topItems[0].total_tokens : 1;
      const chartEl = document.getElementById('chartContainer');
      
      chartEl.innerHTML = topItems.map(item => {{
        const pct = Math.max(5, Math.round((item.total_tokens / maxVal) * 100));
        return `
          <div class="space-y-1 cursor-pointer group" onclick="showDetails('${{item.conversation_id}}')">
            <div class="flex items-center justify-between text-xs">
              <span class="font-medium text-[var(--foreground)] group-hover:text-[var(--primary)] transition-colors truncate max-w-sm" title="${{item.title}}">
                ${{item.title || '(بدون عنوان)'}}
              </span>
              <span class="font-mono text-[11px] font-semibold text-[var(--primary)] ml-2 whitespace-nowrap">
                ${{fmt(item.total_tokens)}}
              </span>
            </div>
            <div class="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden flex">
              <div class="bg-gradient-to-r from-sky-500 to-indigo-500 h-full rounded-full transition-all duration-300" style="width: ${{pct}}%"></div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function render() {{
      const q = document.getElementById('searchInput').value.toLowerCase().trim();
      let filtered = allData.filter(item => {{
        if (!q) return true;
        return (item.conversation_id && item.conversation_id.toLowerCase().includes(q)) ||
               (item.title && item.title.toLowerCase().includes(q));
      }});

      // KPIs
      const totalInput = allData.reduce((acc, x) => acc + (x.input_tokens || 0), 0);
      const totalOutput = allData.reduce((acc, x) => acc + (x.output_tokens || 0), 0);
      const totalCache = allData.reduce((acc, x) => acc + (x.cache_read_tokens || 0), 0);

      document.getElementById('statTotal').textContent = fmt(totalInput + totalOutput);
      document.getElementById('statInput').textContent = fmt(totalInput);
      document.getElementById('statOutput').textContent = fmt(totalOutput);
      document.getElementById('statCache').textContent = fmt(totalCache);
      document.getElementById('countBadge').textContent = `${{filtered.length}} از ${{allData.length}} گفتگو`;

      renderChart(allData);

      // Sort
      filtered.sort((a, b) => {{
        let vA = a[sortCol];
        let vB = b[sortCol];
        if (typeof vA === 'string') {{
          return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
        }}
        return sortAsc ? (vA - vB) : (vB - vA);
      }});

      // Indicators
      document.querySelectorAll('th.sortable span').forEach(s => s.textContent = '');
      const ind = document.getElementById(`sort_${{sortCol}}`);
      if (ind) ind.textContent = sortAsc ? ' ▲' : ' ▼';

      // Table
      const tbody = document.getElementById('tableBody');
      if (filtered.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-xs text-[var(--muted-foreground)]">موردی یافت نشد</td></tr>`;
        return;
      }}

      tbody.innerHTML = filtered.map(item => `
        <tr class="hover:bg-[var(--card-hover)] transition-colors clickable-row" onclick="showDetails('${{item.conversation_id}}')">
          <td class="py-2.5 px-3 max-w-xs">
            <div class="font-medium text-[var(--foreground)] hover:text-[var(--primary)] transition-colors truncate" title="${{item.title}}">
              ${{item.title || '(بدون عنوان)'}}
            </div>
            <div class="text-[10px] text-[var(--muted-foreground)] font-mono mt-0.5 truncate">
              ${{item.conversation_id}}
            </div>
          </td>
          <td class="py-2.5 px-2 text-center font-mono text-[var(--muted-foreground)]">${{item.turn_count}}</td>
          <td class="py-2.5 px-2 text-right font-mono text-[var(--foreground)]">${{fmt(item.input_tokens)}}</td>
          <td class="py-2.5 px-2 text-right font-mono text-[var(--foreground)]">${{fmt(item.output_tokens)}}</td>
          <td class="py-2.5 px-2 text-right font-mono font-semibold text-[var(--primary)]">${{fmt(item.total_tokens)}}</td>
          <td class="py-2.5 px-2 text-right font-mono text-[var(--success)]">${{fmt(item.cache_read_tokens)}}</td>
        </tr>
      `).join('');
    }}

    document.getElementById('closeModalBtn').addEventListener('click', () => {{
      document.getElementById('detailModal').classList.add('hidden');
    }});

    document.getElementById('detailModal').addEventListener('click', (e) => {{
      if (e.target.id === 'detailModal') {{
        document.getElementById('detailModal').classList.add('hidden');
      }}
    }});

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') {{
        document.getElementById('detailModal').classList.add('hidden');
      }}
    }});

    document.querySelectorAll('th.sortable').forEach(th => {{
      th.addEventListener('click', () => {{
        const col = th.getAttribute('data-col');
        if (sortCol === col) {{
          sortAsc = !sortAsc;
        }} else {{
          sortCol = col;
          sortAsc = (col === 'title');
        }}
        render();
      }});
    }});

    document.getElementById('searchInput').addEventListener('input', render);
    render();
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report generated at {output_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", required=True, help="Output HTML path")
    args = parser.parse_args()

    data = get_all_conversations()
    generate_html_report(data, args.output)

if __name__ == "__main__":
    main()
