load("@rules_java//java:java_binary.bzl", "java_binary")
load("@rules_java//java:java_import.bzl", "java_import")

java_import(
    name = "benchmarks",
    jars = [
        "lib/renaissance-gpl-0.14.1.jar",
        "lib/dacapo.jar",
        "lib/async-profiler.jar",
    ],
)

java_binary(
    name = "saraswati",
    srcs = glob(["src/main/java/saraswati/*.java", "src/main/java/saraswati/async/*.java"]),
    main_class = "saraswati.Saraswati",
    runtime_deps = ["@grpc-java//netty"],
    deps = ["//:benchmarks","//src/main/proto/saraswati:saraswati_service_java_protos", "@grpc-java//api", "//src/main/proto/saraswati:saraswati_service_java_grpc"],
)

