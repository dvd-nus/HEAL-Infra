from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.aws.compute import EC2, ECR, ECS, Fargate, EC2AutoScaling, EC2Instances
from diagrams.aws.database import RDS, DocumentDB, ElastiCache, RDSMysqlInstance, DocumentdbMongodbCompatibility
from diagrams.aws.network import ELB
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.aws.network import CF, Route53
from diagrams.aws.storage import S3

edges = {
    "push": Edge(label="on push", style="dotted", color="black"),
    "success": Edge(label="on success", style="dotted", color="black"),
    "upload": Edge(label="push", color="black"),
    "autoscaling": Edge(label="autoscale", style="dotted", color="green")
}


def _get_front_end_bucket():
    return S3("S3 Private Bucket")


def _get_backend_ecr():
    return ECR("ECR Container Registry")


def _get_github_actions_lint_test():
    return GithubActions("Lint + Test")


def _get_github_actions_build():
    return GithubActions("Build")


services = [
    {
        "label": "auth",
        "path": "/auth",
        "name": "Auth"
    },
    # {
    #     "label": "staff",
    #     "path": "/staff",
    #     "name": "Staff"
    # },
    {
        "label": "catalog",
        "path": "/services",
        "name": "Catalog"
    },
    {
        "label": "billing",
        "path": "/bliing",
        "name": "Billing"
    },
    {
        "label": "others",
        "path": "/*",
        "name": "Others"
    },
]

with Diagram("\n\n\nAWS", filename="web_service", show=False, direction="TB"):
    front_end_bucket = _get_front_end_bucket()
    backend_ecr = _get_backend_ecr()

    dns = Route53("www.heal.com")
    cf = CF("CloudFront")

    elbs = []

    with Cluster("ECS Cluster"):
        for service in services:
            with Cluster(service["name"] + " Service", direction="TB"):
                _elb = ELB("ALB " + service["label"])
                _asg = EC2Instances('Auto Scaling \n EC2 Instances')
                _ecs = ECS("ECS Service - \n" + service["label"])

                _elb >> Edge(label="distributes") >> _asg

                [_asg, _elb] << Edge(label="manages", style="dotted") << _ecs

                _ecs << backend_ecr
                service["elb"] = _elb
                service["asg"] = _asg

                if (service["label"] == 'catalog'):
                    _asg - DocumentdbMongodbCompatibility("")

                if (service["label"] == 'auth'):
                    _asg - RDSMysqlInstance("")

    dns >> cf
    cf >> Edge(label="FrontEnd") >> front_end_bucket

    for service in services:
        cf >> Edge(label="/api" + service["path"]) >> service["elb"]

with Diagram("CI 1", show=False, direction="LR"):
    github_actions_lint_test = _get_github_actions_lint_test()
    github_actions_build = _get_github_actions_build()

    front_end_bucket = _get_front_end_bucket()
    front_end_repo = Github("FrontEnd")


    coveralls = Custom("Coveralls", "./custom_logos/coveralls.png")
    sonarcloud = Custom("SonarCloud", "./custom_logos/sonarcloud.png")

    front_end_repo >> \
        edges["push"] >> github_actions_lint_test >>\
        edges["success"] >> github_actions_build >>\
        edges["upload"] >> front_end_bucket

    github_actions_lint_test >> Edge(label="push coverage", color="azure4") >> coveralls
    github_actions_lint_test >> Edge(label="push static code analysis", color="azure4") >> sonarcloud

with Diagram("CI 2", show=False, direction="LR"):
    github_actions_lint_test = _get_github_actions_lint_test()
    github_actions_build = _get_github_actions_build()

    backend_ecr = _get_backend_ecr()
    backend_end_repo = Github("BackEnd")

    coveralls = Custom("Coveralls", "./custom_logos/coveralls.png")
    sonarcloud = Custom("SonarCloud", "./custom_logos/sonarcloud.png")
    zap = Custom("Zap", './custom_logos/zap.png')
    dc = Custom("Dependency Check", './custom_logos/dc.png')

    backend_end_repo >>\
        edges["push"] >> github_actions_lint_test >>\
        edges["success"] >> github_actions_build >>\
        edges["upload"] >> backend_ecr

    github_actions_lint_test >> Edge(label="push coverage", color="azure4") >> coveralls
    github_actions_lint_test >> Edge(label="push static code analysis", color="azure4") >> sonarcloud

    github_actions_lint_test >> Edge(label="run Zap", color="azure4") >> zap
    github_actions_lint_test >> Edge(label="trigger Dependency Check", color="azure4") >> dc
