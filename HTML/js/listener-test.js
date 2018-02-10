var sub = new NchanSubscriber("http://localhost:8081/sub?id=system_stats", 'eventsource')
sub.start();
sub.on("message", function(message, message_metadata) {
    console.log(message);
 });

