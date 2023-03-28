To use as a service

  cp backend.service /lib/systemd/system/
  systemctl daemon-reload
  systemctl enable backend
  systemctl start backend
