
resource "aws_iam_openid_connect_provider" "eks" {
  url = var.cluster_oidc_issuer_url

  client_id_list = [
    "sts.amazonaws.com"
  ]

  tags = {
    Name = "${var.project_name}-eks-oidc"
  }
}


data "aws_iam_policy_document" "controller_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.eks.arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(var.cluster_oidc_issuer_url, "https://", "")}:aud"

      values = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub"

      values = [
        "system:serviceaccount:kube-system:aws-load-balancer-controller"
      ]
    }
  }
}

resource "aws_iam_role" "controller" {
  name               = "${var.project_name}-aws-load-balancer-controller"
  assume_role_policy = data.aws_iam_policy_document.controller_assume_role.json

  tags = {
    Name = "${var.project_name}-aws-load-balancer-controller"
  }
}

resource "aws_iam_policy" "controller" {
  name        = "${var.project_name}-aws-load-balancer-controller"
  description = "Permissions for the AWS Load Balancer Controller"

  policy = file("${path.module}/iam_policy.json")
}

resource "aws_iam_role_policy_attachment" "controller" {
  role       = aws_iam_role.controller.name
  policy_arn = aws_iam_policy.controller.arn
}
