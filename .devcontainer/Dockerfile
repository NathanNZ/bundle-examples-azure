FROM mcr.microsoft.com/devcontainers/python:3.12

# Terraform & xdg-utils (to support the OAuth2 login page)
RUN wget -O- https://apt.releases.hashicorp.com/gpg \
  | gpg --dearmor \
  | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg >/dev/null \
  && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | tee /etc/apt/sources.list.d/hashicorp.list \
  # Required to pop the OAuth2 login page
  && apt-get update && apt-get install -y terraform xdg-utils \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Databricks
RUN curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh