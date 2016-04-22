# /usr/lib/pypy/bin/pypy-c  -m cProfile -o obin_profile.prof /home/gloryofrobots/develop/languages/obin/obin/src/script/proto/obin/targetobin.py /home/gloryofrobots/develop/languages/obin/obin/src/script/proto/obin/test/obin/main.obn
python  -m cProfile -o obin_profile.prof /home/gloryofrobots/develop/languages/obin/obin/obin_py/targetobin.py /home/gloryofrobots/develop/languages/obin/obin/obin_py/test/obin/main.obn

# gprof2dot -f pstats obin_profile.prof | dot -Tpng -o obin_profile.png
# runsnake obin_profile.prof
# pip install pyprof2calltree
#pyprof2calltree -i obin_profile.prof -k
