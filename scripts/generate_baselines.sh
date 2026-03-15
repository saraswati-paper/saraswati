elems="akka-uct gauss-mix philosophers als  graphchi pmd avrora  h2  reactors batik  jme  rx-scrabble biojava  jython  scala-doku chi-square log-regression scala-kmeans dec-tree luindex scala-stm-bench7 dotty  lusearch scrabble finagle-chirper mnemonics sunflow finagle-http xalan fj-kmeans naive-bayes zxing fop  page-rank future-genetic par-mnemonics"
for bench in $elems; do
    python3 $PWD/scripts/generate_experiments.py --exp_path=./data/baseline/$bench/ --java_path=$PWD/jdk/bin/java --python_path=$PWD/venv/bin/python --server_config=$PWD/server-configs/profiler_$bench.json --baseline
done
