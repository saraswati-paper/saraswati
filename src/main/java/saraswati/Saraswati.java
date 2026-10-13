package saraswati;
import io.grpc.Channel;
import io.grpc.Grpc;
import io.grpc.InsecureChannelCredentials;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Saraswati{
    public Saraswati(){
	throw new UnsupportedOperationException("Saraswati cannot be instantiated");
    }

    private static long pid;
    private static SaraswatiServiceGrpc.SaraswatiServiceBlockingStub blockingStub;
    private static final Logger logger = Logger.getLogger(Saraswati.class.getName());
    
    /** Asks the server if it can run */
    public static boolean startRequest(){
	StartRequest request = StartRequest.newBuilder().setPid(Saraswati.pid).build();
	StartResponse response;	 
	try {
	    response = Saraswati.blockingStub.start(request);
	    return response.getCanRun();
	}catch(StatusRuntimeException e){
	    logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
	    return false;
	}catch(Exception e){
	    System.out.println(e);
	    return false;
	}
    }

    /** Notifies the server that the connected application has finished */
    public static void finishedNotification(){
	FinishedNotification notification = FinishedNotification.newBuilder().setPid(Saraswati.pid).build();
	try {
	    Saraswati.blockingStub.finished(notification);	  
	}catch(StatusRuntimeException e){
	    logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
	    return;
	}catch(Exception e){
	    System.out.println(e);
	    return;
	}
    }

    /** Connects to the server */
    public static boolean connect(String appName) {
	try {
	    ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", 50051).usePlaintext().build();    
	    Saraswati.blockingStub = SaraswatiServiceGrpc.newBlockingStub(channel);
	    Saraswati.pid = ProcessHandle.current().pid();
	    //Sending a Connection Request to set up Python Server State
	    ConnectionRequest request = ConnectionRequest.newBuilder().setApplicationName(appName).setPid(Saraswati.pid).build();
	    ConnectionResponse response;
	    response = blockingStub.connect(request);
	    return response.getIsAvailable();
	}catch (StatusRuntimeException e) {
	    return false;
	}
    }

    public static void main(String[] args){}
}

