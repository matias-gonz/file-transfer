ntftp_protocol = Proto("NTFTP",  "NTFTP Protocol")

packet_number = ProtoField.uint32("ntftp.packet_number", "Packet Number", base.DEC)
response_code = ProtoField.uint8("ntftp.response_code", "Response Code", base.DEC)
request_code = ProtoField.uint8("ntftp.request_code", "Request Code", base.DEC)
file_name = ProtoField.string("ntftp.file_name", "File Name", base.UNICODE)
file_data = ProtoField.string("ntftp.file_data", "File Data")

ntftp_protocol.fields = {
  packet_number,
  request_code, file_name,
  response_code,
  file_data,
}

function ntftp_protocol.dissector(buffer, pinfo, tree)
  length = buffer:len()
  if length == 0 then return end

  pinfo.cols.protocol = ntftp_protocol.name

  local subtree = tree:add(ntftp_protocol, buffer(), "NTFTP Protocol Data")

  local pkt_num = buffer(0, 4):uint()
  local t = subtree:add(packet_number, buffer(0, 4))
  if pkt_num == 0 then
    if length == 5 then
      t:append_text(" (SERVER_RESPONSE)")
  
      local t = subtree:add(response_code, buffer(4, 1))
      local res_code = buffer(4, 1):uint()
      local s = " ("
      if res_code == 0 then s = s .. "ALL_OK"
      elseif res_code == 1 then s = s .. "ERROR_OPENING_FILE"
      else s = s .. "INVALID_REQUEST" end

      t:append_text(s .. ")")

    else
      t:append_text(" (CLIENT_REQUEST)")

      local t = subtree:add(request_code, buffer(4, 1))

      local req_code = buffer(4, 1):uint()
      local s = " ("
      if req_code == 1 then s = s .. "DOWNLOAD" else s = s .. "UPLOAD" end

      t:append_text(s .. ")")

      subtree:add(file_name, buffer(5, length - 5))
    end
  else
    if length == 4 then
      t:append_text(" (ACK)")
    else
      subtree:add(file_data, "(" .. tostring(length - 4) .. " bytes)")
    end
  end
end

local udp_port = DissectorTable.get("udp.port")
udp_port:add(6543, ntftp_protocol)
