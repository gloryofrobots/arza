def float_mul_test(x,y):
    return "CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(%f), OFloat(%f))),  %f);" %(x,y, x*y)

def float_div_test(x,y):
    return "CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(%f), OFloat(%f))),  %f);" %(x,y, x/y)


print float_mul_test(234.56, 3434.4554)
print float_mul_test(1.56, 0.04554)
print float_mul_test(-99, 43.090909)
print float_mul_test(-10000234.1213, -8.000000)
print float_mul_test(42, 0)
print float_mul_test(1, 42.1)
print "DIVIDE"
print float_div_test(234.56, 3434.4554)
print float_div_test(1.56, 0.04554)
print float_div_test(-99, 43.090909)
print float_div_test(-10000234.1213, -8.000000)
print float_div_test(42, 1)
print float_div_test(1, 42.1)
