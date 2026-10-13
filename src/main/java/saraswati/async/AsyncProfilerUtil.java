package saraswati.async;
import java.time.Duration;
import java.time.Instant;
import one.profiler.AsyncProfiler;
import one.profiler.Events;

/** Utility wrapper around the async-profiler to start and stop it as needed. */
public final class AsyncProfilerUtil {
  // private static final Duration asyncPeriod =
  //     Duration.ofMillis(Integer.parseInt(System.getProperty("saraswati.async.period", "2")));
    private static final Duration asyncPeriod = Duration.ofMillis(Integer.parseInt(System.getProperty("saraswati.async.period", "100")));
    //private static final Duration asyncPeriod = Duration.ofMillis(Integer.parseInt(System.getProperty("saraswati.async.period", "2"))); //Changed from 100ms to help rx-scrabble out
    private static final Duration asyncCollectionPeriod =
      Duration.ofMillis(
          Integer.parseInt(System.getProperty("saraswati.async.collection.period", "500")));
  private static boolean asyncRunning = false;
  private static Instant last = Instant.now();

  public static synchronized String readAsyncProfiler() {
    Instant now = Instant.now();
    if (Duration.between(last, now).toMillis() > asyncCollectionPeriod.toMillis()) {
      if (!asyncRunning) {
        AsyncProfiler.getInstance().start(Events.CPU, asyncPeriod.getNano());
        asyncRunning = true;
      }
      AsyncProfiler.getInstance().stop();
      String traces = AsyncProfiler.getInstance(String.join("/", System.getProperty("saraswati.library.path"), "libasyncProfiler.so")).dumpRecords();
      AsyncProfiler.getInstance().resume(Events.CPU, asyncPeriod.getNano());
      last = now;
      return traces;
    }
    return "0,-1,dummy\n";
  }

  private AsyncProfilerUtil() {}
}

