package saraswati;

import org.dacapo.harness.Callback;
import org.dacapo.harness.CommandLineArgs;
import org.dacapo.parser.Config;

/** {@link Callback} for dacapo that wraps usage of the {@link SampleCollector}. */
public class SaraswatiDacapoCallback extends Callback {
  private final SampleCollector collector;
  private final ProfilerCollector profiler;

  public SaraswatiDacapoCallback(CommandLineArgs args) {
    super(args);
    if(System.getProperty("saraswati.use.jrapl") != null){
	collector = new RaplSampleCollector();
    }else{
	collector = new PowercapSampleCollector();
    }
    if(System.getProperty("saraswati.skip.profiler") == null)
	profiler = new ProfilerCollector();
    else
	profiler = null;
  }

  @Override
  public void start(String benchmark) {
    super.start(benchmark);
    collector.start();
    if(profiler != null)
	profiler.start();
  }

  @Override
  public void stop(long w) {
    super.stop(w);
    collector.stop();
    if(profiler != null)
	profiler.stop();
    collector.write_iter();
    if(profiler != null)
	profiler.write_iter();
    Saraswati.finishedNotification();
  }

  @Override
  public boolean runAgain() {
    // if we have run every iteration, dump the data and terminate
    // if (!super.runAgain()) {
    if(!Saraswati.startRequest()){
      System.out.println("dumping data");
      collector.dump();
      if(profiler != null)
	  profiler.dump();
      Saraswati.finishedNotification();
      return false;
    } else {
      return true;
    }
  }


    @Override
    public void init(Config config){
	//Dacapo runs the benchmark immediately after the init finishes, so we have to wait on the request here
	super.init(config);
	Saraswati.connect(config.name);
	Saraswati.startRequest();
    }
    
}

