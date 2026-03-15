package saraswati;
import saraswati.async.*;
import saraswati.async.StackTraceSample;
import java.time.Instant;

import static java.util.stream.Collectors.joining;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.IntStream;
import java.util.stream.Collectors;

public final class ProfilerCollector implements SampleCollector{

    private final ArrayList<StackTraceSample> samples = new ArrayList<>();
    private final ExecutorService executor;
    private volatile boolean isRunning = false;
    private Future<ArrayList<StackTraceSample>> sampleFuture;
    private int iteration = 1;

    private long app_start;
    private long app_stop;
    
    public ProfilerCollector() {
	executor = Executors.newSingleThreadExecutor();
    }

  private static long getMonotonicTimestamp() {
    return MonotonicTimestamp.getInstance(
            String.join("/", System.getProperty("saraswati.library.path"), "libMonotonic.so"))
        .getMonotonicTimestamp();
  }
    
    public void start(){
	app_start = getMonotonicTimestamp();
	isRunning = true;
	sampleFuture =
	    executor.submit(
			    () -> {
				ArrayList<StackTraceSample> samples = new ArrayList<>();
				while (isRunning) {
				    samples.addAll((new AsyncProfilerSample(Instant.now(), AsyncProfilerUtil.readAsyncProfiler(), this.iteration)).getSamples());
				    try {
					Thread.sleep(100);
				    } catch (Exception e) {
					System.out.println("couldn't sleep!");
					e.printStackTrace();
				    }
				}
				return samples;
			    });
    }
    
    public void stop(){
	isRunning = false;
	try{
	    samples.addAll(sampleFuture.get());
	}catch(Exception e){
	    System.err.println("couldn't get profiling data!");
	    e.printStackTrace();
	}
	app_stop = getMonotonicTimestamp();
	iteration++;
    }



    
    public void write_iter(){
	//Get the finished iteration's samples
	int prev_iter = this.iteration - 1;
	List<StackTraceSample> iter_samples = samples.stream().filter(s->s.getIteration() == prev_iter).collect(Collectors.toList());
	//long start_time = this.app_start, stop_time = this.app_stop;
	//List<StackTraceSample> iter_samples = samples.stream().filter(s->{System.err.printf("%d&&%d&&%d%n", start_time, s.getTimestamp(), stop_time); return s.getTimestamp() >= start_time && s.getTimestamp() <= stop_time;}).collect(Collectors.toList());
	if (iter_samples.isEmpty()) {
	    System.out.println("no profiler samples collected!");
	    return;
	}
	try {
	    String filename = "profile_" + prev_iter + ".csv";
	    PrintWriter writer =
		new PrintWriter(
				new BufferedWriter(
						   new FileWriter(
								  String.join(
									      "/", System.getProperty("saraswati.output.directory"), filename))));
	    writer.println(String.join(",","timestamp","id","trace"));
	    for(StackTraceSample s : iter_samples){
		writer.println(String.join(",",
					   ""+s.getTimestamp(),
					   s.getId()+"",
					   s.getStackTrace()));
	    }
	    writer.close();
	} catch (IOException e) {
	    System.out.println("Unable to write Saraswati profile data!");
	    e.printStackTrace();
	}
    }
    
    public void dump(){
	//Profiler just needs to shutdown the threadpool
	executor.shutdown();
    }
}
