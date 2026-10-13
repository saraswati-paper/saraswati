package saraswati.async;
import saraswati.async.StackTraceSample;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;

/** Sample collection of async-profiler records. */
public final class AsyncProfilerSample{
  private final Instant timestamp;
  private final String records;
  private final int iteration;
    
  public AsyncProfilerSample(Instant timestamp, String records, int iteration) {
    this.timestamp = timestamp;
    this.records = records;
    this.iteration = iteration;
  }

  /** Return the stored timestamp. */
  public Instant getTimestamp() {
    return timestamp;
  }

  /** Parse and return the jiffies from the stat strings. */
  public Collection<StackTraceSample> getSamples() {
    ArrayList<StackTraceSample> samples = new ArrayList<>();
    for (String record : records.split("\n")) {
      String[] entries = record.split(",");
      //Instant timestamp = Instant.ofEpochMilli(Long.parseLong(entries[0]));
      if(entries[0].equals(""))
	  continue;
      long timestamp = Long.parseLong(entries[0]);
      long id = Long.parseLong(entries[1]);
      String stackTrace = entries[2];
      samples.add(new StackTraceSample(timestamp, id, stackTrace, this.iteration));
    }
    return samples;
  }
}

