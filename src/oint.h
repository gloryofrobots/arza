#ifndef OBIN_OINT_H_
#define OBIN_OINT_H_

syx_bool
SYX_SMALL_INTEGER_MUL_OVERFLOW (syx_int32 a, syx_int32 b)
{
#ifdef HAVE_INT64_T
  syx_int64 res = (syx_int64)a * (syx_int64)b;
  if ((res > INT_MAX) || (res < INT_MIN))
    return TRUE;
#else
  if (a > 0)
    {
      if (b > 0)
        {
          if (a > (INT_MAX / b))
            return TRUE;
        }
      else
        {
          if (b < (INT_MIN / a))
            return TRUE;
        }
    }
  else
    {
      if (b > 0)
        {
          if (a < (INT_MIN / b))
            return TRUE;
        }
      else
        {
          if ( (a != 0) && (b < (INT_MAX / a)))
            return TRUE;
        }
    }
#endif

  return FALSE;
}

/*! TRUE if an overflow occurs when shifting a by b */
syx_bool
SYX_SMALL_INTEGER_SHIFT_OVERFLOW (syx_int32 a, syx_int32 b)
{
  /* Thanks to Sam Philips */
  syx_int32 i;
  syx_int32 sval;

  if (b <= 0)
    return FALSE;

  i = 0;
  sval = abs(a);

  while (sval >= 16)
    {
      sval = sval >> 4;
      i += 4;
    }

  while (sval != 0)
    {
      sval = sval >> 1;
      i++;
    }

  if ((i + b) > 30)
    return TRUE;

  return FALSE;
}



#endif /* OINT_H_ */
