load("@protobuf//bazel:java_proto_library.bzl", "java_proto_library")
load("@grpc-java//:java_grpc_library.bzl", "java_grpc_library")
load("@protobuf//bazel:proto_library.bzl", "proto_library")
#load("@bazel_tools//src/main/protobuf:proto_library.bzl", "proto_library")

proto_library(
    name = "saraswati_service_protos",
    visibility = ["//visibility:public"],
    srcs = ["saraswati_service.proto"],
)

java_proto_library(
    name = "saraswati_service_java_protos",
    visibility = ["//visibility:public"],
    deps = [":saraswati_service_protos"],
)

java_grpc_library(
    name = "saraswati_service_java_grpc",
    visibility = ["//visibility:public"],
    srcs = [":saraswati_service_protos"],
    deps = [":saraswati_service_java_protos"]
)
