#!/bin/bash
cd /home/kavia/workspace/code-generation/aws-bedrock-agent-query-platform-88993-89003/frontend_streamlit_interface
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

