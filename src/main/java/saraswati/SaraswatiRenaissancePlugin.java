package saraswati;

import org.renaissance.Plugin;

/** {@link Plugin} for renaissance that wraps usage of the {@link SampleCollector}. */
public class SaraswatiRenaissancePlugin
    implements Plugin.BeforeBenchmarkTearDownListener,
        Plugin.AfterOperationSetUpListener,
	Plugin.BeforeOperationTearDownListener,
	Plugin.ExecutionPolicy,
	Plugin.BeforeBenchmarkSetUpListener{
  private SampleCollector collector;
  private ProfilerCollector profiler;
    
  @Override
  public void beforeBenchmarkSetUp(String benchmark){
      if(System.getProperty("saraswati.use.jrapl") != null){
	  collector = new RaplSampleCollector();
      }else{
	  collector = new PowercapSampleCollector();
      }
      if(System.getProperty("saraswati.skip.profiler") == null)
	  profiler = new ProfilerCollector();
      else
	  profiler = null;
      boolean response = Saraswati.connect(benchmark);
      System.out.println("CONNECTED? "+response);
  }
    
  @Override
  public void afterOperationSetUp(String benchmark, int opIndex, boolean isLastOp) {
    collector.start();
    if(profiler != null)
	profiler.start();
  }

  @Override
  public void beforeOperationTearDown(String benchmark, int opIndex, long durationNanos) {
    collector.stop();
    if(profiler != null)
	profiler.stop();
    collector.write_iter();
    if(profiler != null)
	profiler.write_iter();
    Saraswati.finishedNotification();
  }

  @Override
  public void beforeBenchmarkTearDown(String benchmark) {
    System.out.println("dumping data");
    collector.dump();
    if(profiler != null)
	profiler.dump();
    Saraswati.finishedNotification();
  }

  @Override
  public boolean canExecute(String benchmark, int opIndex){
      boolean response = Saraswati.startRequest();
      System.out.println("CAN RUN? " + response);
      return response;
  }

  @Override
  public boolean isLast(String benchmark, int opIndex){
      return false;
  }
}
