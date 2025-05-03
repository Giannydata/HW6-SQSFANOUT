import aws_cdk as core
import aws_cdk.assertions as assertions

from sqs_fanout.sqs_fanout_stack import SqsFanoutStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sqs_fanout/sqs_fanout_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SqsFanoutStack(app, "sqs-fanout")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
