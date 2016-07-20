pypy -m cProfile -o debinfo/obin_profile.prof targetobin.py test/obin/main.obn

# gprof2dot -f pstats debinfo/obin_profile.prof | dot -Tpng -o debinfo/obin_profile.png
# runsnake debinfo/obin_profile.prof
# pip install pyprof2calltree
#pyprof2calltree -i debinfo/obin_profile.prof -k
