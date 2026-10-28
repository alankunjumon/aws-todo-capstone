# 
# ============================================
# 1. CREATE THE EKS CLUSTER(
# ============================================

resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-eks"
  role_arn = var.cluster_role_arn

  vpc_config {
    subnet_ids = var.private_subnet_ids

    endpoint_private_access = true
    endpoint_public_access  = true

    public_access_cidrs = var.cluster_endpoint_public_access_cidrs
  }

  tags = {
    Name = "${var.project_name}-eks"
  }
}

# Launch template for EKS worker nodes
resource "aws_launch_template" "nodes" {
  name_prefix = "${var.project_name}-eks-nodes-"

  vpc_security_group_ids = [
    var.node_security_group_id,
    aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
  ]
}

# Allow EKS control plane to reach worker-node kubelets
resource "aws_vpc_security_group_ingress_rule" "cluster_to_nodes_kubelet" {
  security_group_id            = var.node_security_group_id
  referenced_security_group_id = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id

  description = "Allow EKS control plane to communicate with worker kubelets"
  ip_protocol = "tcp"
  from_port   = 10250
  to_port     = 10250
}

# ============================================
# 2. CREATE THE MANAGED WORKER NODE GROUP
# ============================================

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-managed-nodes"
  node_role_arn   = var.node_role_arn

  launch_template {
    id      = aws_launch_template.nodes.id
    version = tostring(aws_launch_template.nodes.latest_version)
  }

  subnet_ids     = var.private_subnet_ids
  instance_types = var.node_instance_types
  capacity_type  = "ON_DEMAND"

  scaling_config {
    desired_size = var.desired_size
    min_size     = var.min_size
    max_size     = var.max_size
  }

  update_config {
    max_unavailable = 1
  }

  tags = {
    Name = "${var.project_name}-managed-nodes"
  }
}
