#!/usr/bin/env bash
#
# Ruleaza fiecare test LRTA* de 10 ori, afiseaza detaliile si salveaza rezumatul in results_lrta.csv

OUT=results_lrta.csv
# header CSV
echo "Test,solved,not_solved,avg_time_s,min_time_s,max_time_s,avg_steps,min_steps,max_steps,avg_pulls,min_pulls,max_pulls,total_time_s" > "$OUT"

for f in tests/*.yaml; do
  name=$(basename "$f")
  echo "=============================="
  echo "🎯  LRTA* Test: $name"
  echo "------------------------------"

  solved=0; not_solved=0
  sum_time=0.0; min_time=9999; max_time=0.0
  sum_steps=0;  min_steps=9999999; max_steps=0
  sum_pulls=0;  min_pulls=9999999; max_pulls=0

  start_all=$(date +%s.%N)
  for i in $(seq 1 10); do
    line=$(python3 main.py "lrta*" --heuristic base "$f" 2>&1 | tail -n1)
    if echo "$line" | grep -q "status: SOLVED"; then
      ((solved++)); icon="✅"
      t=$(echo "$line" | sed -n 's/.*time: \([0-9.]*\)s.*/\1/p')
      st=$(echo "$line" | sed -n 's/.*steps: \([0-9]*\).*/\1/p')
      pl=$(echo "$line" | sed -n 's/.*pulls: \([0-9]*\).*/\1/p')
      sum_time=$(awk "BEGIN{printf \"%.6f\", $sum_time + $t}")
      (( sum_steps += st )); (( sum_pulls += pl ))
      min_time=$(awk "BEGIN{print ($t < $min_time ? $t : $min_time)}")
      max_time=$(awk "BEGIN{print ($t > $max_time ? $t : $max_time)}")
      (( min_steps = st < min_steps ? st : min_steps ))
      (( max_steps = st > max_steps ? st : max_steps ))
      (( min_pulls = pl < min_pulls ? pl : min_pulls ))
      (( max_pulls = pl > max_pulls ? pl : max_pulls ))
    else
      ((not_solved++)); icon="❌"
      t=0.000000; st=0; pl=0
    fi
    printf "  %2d) %s time: %5ss  steps: %5d  pulls: %d\n" \
      "$i" "$icon" "$t" "$st" "$pl"
  done
  end_all=$(date +%s.%N)
  total_time=$(awk "BEGIN{printf \"%.6f\", $end_all - $start_all}")
  avg_time=$(awk "BEGIN{printf \"%.6f\", $sum_time/10}")
  avg_steps=$(( sum_steps / 10 )); avg_pulls=$(( sum_pulls / 10 ))

  echo "------------------------------"
  echo "📊  Rezumat LRTA* pentru $name:"
  echo "   ✔️ Solved     : $solved"
  echo "   ❌ Not solved : $not_solved"
  echo "   �⏱ Total time (10 runs): ${total_time}s"
  echo "   ⏱ Avg time   : ${avg_time}s (min ${min_time}s, max ${max_time}s)"
  echo "   🔢 Avg steps  : ${avg_steps} (min ${min_steps}, max ${max_steps})"
  echo "   📈 Avg pulls  : ${avg_pulls} (min ${min_pulls}, max ${max_pulls})"
  echo ""

  # scrie linia CSV
  echo "$name,$solved,$not_solved,$avg_time,$min_time,$max_time,$avg_steps,$min_steps,$max_steps,$avg_pulls,$min_pulls,$max_pulls,$total_time" \
    >> "$OUT"
done

echo "✅ Datele LRTA* au fost salvate în '$OUT'"
