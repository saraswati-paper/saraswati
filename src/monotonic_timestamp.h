#include <jni.h>

#ifndef _Included_saraswati_MonotonicTimestamp
#define _Included_saraswati_MonotonicTimestamp
#ifdef __cplusplus
extern "C" {
#endif

JNIEXPORT jlong JNICALL Java_saraswati_MonotonicTimestamp_getMonotonicTimestamp
  (JNIEnv *, jclass);

#ifdef __cplusplus
}
#endif
#endif
