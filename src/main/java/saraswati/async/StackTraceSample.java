package saraswati.async;
import java.time.Instant;

/** Sample of a thread's current executing trace. */
public final class StackTraceSample {
  private final long timestamp;
  private final long id;
  private final String stackTrace;
  private final int iteration;
    
  public StackTraceSample(long timestamp, long id, String stackTrace, int iteration) {
    this.timestamp = timestamp;
    this.id = id;
    this.stackTrace = stackTrace;
    this.iteration = iteration;
  }

  /** Returns the stored timestamp. */
  public long getTimestamp() {
    return timestamp;
  }

  /** Returns the executing thread's id. */
  public long getId() {
    return id;
  }

  /** Returns the executing stack trace. */
  public String getStackTrace() {
    return stackTrace;
  }

  /** Returns the executing stack trace. */
  public int getIteration() {
    return iteration;
  }
}
