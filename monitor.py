import streamlit as st
import random
import pandas as pd
import time
import dns.resolver
from getstat import get_server_stats
from datetime import datetime
from dns_control import get_list, update_dns
import subprocess

if 'inactive_start_time' not in st.session_state:
    st.session_state.inactive_start_time = None
if 'inactive_duration' not in st.session_state:
    st.session_state.inactive_duration = 0

# 模拟获取 Kubernetes 集群节点信息
def get_kubernetes_nodes():
    mninfo = get_server_stats("NODEIP")
    nodes = [
        {
            "name": "Master Node（主节点）",
            "status": mninfo.get("status","N/A"),
            "latency": mninfo.get("latency",0),
            "load": mninfo.get("cpu_load",0),
            "memory": mninfo.get("memory_usage",0),
            "ip": "NODEIP",
            "link": "http://cloud.huxundao.com"
        },
        {
            "name": "Worker Node 1（工作节点1）",
            "status": "NotReady",
            "latency": random.randint(1000, 2000),
            "load": random.randint(10, 100),
            "memory": 30,
            "ip": "",
            "link": ""
        },
        {
            "name": "Worker Node 2（工作节点2）",
            "status": "NotReady",
            "latency": random.randint(1000, 2000),
            "load": random.randint(10, 100),
            "memory": 30,
            "ip": "",
            "link": ""
        },
        {
            "name": "Worker Node 3（工作节点3）",
            "status": "NotReady",
            "latency": random.randint(1000, 2000),
            "load": random.randint(10, 100),
            "memory": 30,
            "ip": "",
            "link": ""
        },
    ]
    return nodes



# 模拟获取热备服务信息
def get_hot_standby_services():
    mninfo = get_server_stats("SERVICEIP")
    print(mninfo)
    services = [
        {
            "name": "Hot Standby Server 1",
            "status": mninfo.get("status","N/A"),
            "latency": mninfo.get("latency",0),
            "load": mninfo.get("cpu_load",0),
            "memory": mninfo.get("memory_usage",0),
            "ip": "SERVICEIP",
            "link": "http://SERVICEIP:9001"
        },
    ]
    return services

def ping_domain(domain):
    try:
        output = subprocess.run(
            ["ping", "-n", "4", domain],  # For Linux/Mac, use ["ping", "-c", "4", domain]
            capture_output=True,
            text=True
        )
        print(output)
        if output.returncode == 0:
            return f"Ping成功:\n{output.stdout}"
        else:
            return f"Ping失败:\n{output.stderr}"
    except Exception as e:
        return f"Ping命令执行失败: {e}"

def parse_ping_output(output):
    if output:
        lines = output.splitlines()
        for line in lines:
            if "平均" in line or "Average" in line:
                return line.split("=")[-1].strip()
    return None

# 切换 DNS
def switch_dns(selected_service):
    try:
        update_dns(selected_service)
        st.success(f"DNS重写成功: {selected_service}")

    except Exception as e:
        st.error(f"DNS重写失败: {e}")


def get_dns_details(domain):
    try:
        return(get_list())
        
    except Exception as e:
        return "查询出错"

# Streamlit 界面
def main():
    st.title("集群监控与自动化故障转移面板")

    st.header("综合监控图表")
    chart_placeholder = st.empty()
    nodes_placeholder3 = st.empty()
    
    # 左右布局
    col1, col2, col3 = st.columns(3)

    with col1:
       
        # 显示 Kubernetes 集群节点信息
        st.header("Kubernetes 集群")
        nodes_placeholder = st.empty()

    with col2:
        
        domain = "cloudapi.huxundao.com"
        st.header("网盘存储 API 状态")
        with st.expander(domain):
            if st.button("刷新API信息"):
                ping_output = ping_domain(domain)
                latency = parse_ping_output(ping_output)
                if latency:
                    st.write(f"latency(ping): {latency}")
                    st.success("服务可用")  # 绿灯
                else:
                    st.write("Ping失败")
                    st.error("服务不可用")  # 红灯
                    
                dns_info = get_dns_details(domain)
                st.write(dns_info)
                
        
                
        
                
    with col3:
    # 显示热备服务信息
        st.header("热备服务")
        nodes_placeholder2 = st.empty()
        

        # 故障转移选项
        st.header("故障转移")
        failover_options = {
            "microK8s Cluster": "NODEIP",
            "Hot Standby Server 1": "SERVICEIP"
        }
        selected_service = st.selectbox("选择要故障转移的服务", list(failover_options.keys()))
        if st.button("执行故障转移"):
            selected_ip = failover_options[selected_service]
            switch_dns(selected_ip)
     # 自动灾备功能开关
    with st.sidebar:
        st.header("自动灾备设置")
        if "auto_disaster_recovery" not in st.session_state:
            st.session_state.auto_disaster_recovery = False
    
        auto_recovery_enabled = st.checkbox("启用自动灾备", value=st.session_state.auto_disaster_recovery)
    
        if auto_recovery_enabled:
            st.session_state.auto_disaster_recovery = True
    
            # 自动灾备规则
            st.subheader("自动灾备规则")
            if "rule" not in st.session_state:
                st.session_state.rule = None
    
            with st.expander("添加或修改自动灾备方案"):
                with st.form(key="add_rule_form"):
                    failover_options = {
                        "microK8s Cluster": "NODEIP",
                        "Hot Standby Server 1": "SERVICEIP"
                    }
                    duration = st.number_input("宕机持续时间 (秒)", min_value=0, value=10)
                    selected_service = st.selectbox("选择要故障转移的服务", list(failover_options.keys()))
                    submit_button = st.form_submit_button("保存规则")
    
                    if submit_button:
                        new_rule = {
                            "duration": duration,
                            "service": failover_options[selected_service],
                            "enabled": True
                        }
                        st.session_state.rule = new_rule
                        st.success("规则已保存！")
    
            # 显示当前规则
            if st.session_state.rule:
                rule = st.session_state.rule
                rule_description = f"当前规则: 当inactive持续 {rule['duration']}秒 时，启用 {rule['service']}"
                st.markdown(f"- {rule_description}")
    
        else:
            st.session_state.auto_disaster_recovery = False
            st.session_state.rule = None
        # 实时更新数据
        if "timestamps" not in st.session_state:
            st.session_state.timestamps = []
            st.session_state.cluster_load = []
            st.session_state.hot_standby_load = []


    
    
    while True:
        # 更新节点信息
        nodes = get_kubernetes_nodes()
        latency1 = int(nodes[0].get('latency','0'))
        nodestatus = nodes[0]['status']
        with nodes_placeholder.container():
            for node in nodes:
                with st.expander(node['name']):
                    latency_color = "green" if node['latency'] < 2000 else "red"
                    load_color = "green" if node['load'] < 80 else "red"
                    memory_color = "green" if node['memory'] < 50 else "red"
                    opacity = "0.5" if node['status'] == "NotReady" else "1"
                    status_icon = "🟢" if node['status'] != "inactive" else "🔴"
                    st.markdown(f"""
                     <div style="background-color: #2e2e2e; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: white; opacity: {opacity};">
                        <strong>{status_icon}节点名称:</strong> {node['name']}<br>
                        <strong>状态:</strong> {node['status']}<br>
                        <strong>IP:</strong> {node['ip']}<br>
                        <strong>MINIO:</strong> <a href="{node['link']}" style="color: white;" target="_blank">dashboard</a><br>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <div>延迟: <span style="color:{latency_color};">{node['latency']}ms</span></div>
                            <div>内存: <span style="color:{memory_color};">{node['memory']}%</span></div>
                            <div>负载: <span style="color:{load_color};">{node['load']}%</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        services = get_hot_standby_services()
        latency2 = int(services[0].get('latency','0'))
        servicestatus = services[0]['status']
        with nodes_placeholder2.container():
            with st.expander("查看服务信息"):
                for service in services:
                    latency_color = "green" if service['latency'] < 2000 else "red"
                    memory_color = "green" if service['memory'] < 80 else "red"
                    load_color = "green" if service['load'] < 50 else "red"
                    status_icon = "🟢" if service['status'] != "inactive" else "🔴"
                    st.markdown(f"""
                    <div style="background-color: #2e2e2e; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: white;">
                        <strong>{status_icon}服务名称:</strong> {service['name']}<br>
                        <strong>状态:</strong> {service['status']}<br>
                        <strong>IP:</strong> {service['ip']}<br>
                        <strong>MINIO:</strong> <a href="{service['link']}" style="color: white;" target="_blank">dashboard</a><br>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <div>延迟: <span style="color:{latency_color};">{service['latency']}ms</span></div>
                            <div>内存: <span style="color:{memory_color};">{service['memory']}%</span></div>
                            <div>负载: <span style="color:{load_color};">{service['load']}%</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with nodes_placeholder3.container():
            if "rule" not in st.session_state:
                st.session_state.rule = None
            if st.session_state.rule:
                # 更新 inactive 状态持续时间
                status_icon = "🟢" if nodestatus != "inactive" else "🔴"

                current_time = time.time()
                if nodestatus == "inactive":
                    if st.session_state.inactive_start_time is None:
                        st.session_state.inactive_start_time = current_time
                    st.session_state.inactive_duration = int(current_time - st.session_state.inactive_start_time)
                else:
                    st.session_state.inactive_start_time = None
                    st.session_state.inactive_duration = 0
                
                rule = st.session_state.rule
                rule_description = f"正在运行的规则：当inactive持续 {rule['duration']}秒 时，启用 {rule['service']}"
                st.info(f"{rule_description} 当前状态：{status_icon}")
                if nodestatus == "inactive":
                    st.info(f"当前inactive已持续 {st.session_state.inactive_duration} 秒")
                # 检查是否超过阈值
                if st.session_state.inactive_duration >= rule['duration']:
                    st.warning("规则触发,开始执行规则...")
                    st.warning(f"启用 {rule['service']}...")
                    if servicestatus == 'inactive':
                        st.error(f"热备服务故障，启动失败")
                    else:
                        st.warning(f"执行DNS转移 {rule['service']}...")
                        switch_dns(rule['service'])
                        st.warning(f"转移完成，测试API cloudapi.huxundao.com...")
                        ping_output = ping_domain("cloudapi.huxundao.com")
                        max_attempts = 10
                        attempt = 0
                        success = False
                        
                        while attempt < max_attempts:
                            ping_output = ping_domain("cloudapi.huxundao.com")
                            if "成功" in ping_output:
                                st.success("规则执行成功,API恢复可用")
                                success = True
                                break
                            else:
                                attempt += 1
                                time.sleep(1)  # 等待一秒后重试
                                st.warning(f"测试API cloudapi.huxundao.com... faild retry {attempt}/{max_attempts}")
                        if not success:
                            st.error("规则执行失败，已达到最大重试次数")
                        
                        
                        

        # 获取当前时间
        current_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.timestamps.append(current_time)
        st.session_state.cluster_load.append(latency1)
        st.session_state.hot_standby_load.append(latency2)

        # 保留最近5分钟的数据
        if len(st.session_state.timestamps) > 60:
            st.session_state.timestamps.pop(0)
            st.session_state.cluster_load.pop(0)
            st.session_state.hot_standby_load.pop(0)

        # 创建数据框
        load_data = pd.DataFrame({
            "时间": st.session_state.timestamps,
            "集群延迟": st.session_state.cluster_load,
            "热备延迟": st.session_state.hot_standby_load
        })

        # 绘制图表
        load_data.set_index("时间", inplace=True)
        chart_placeholder.line_chart(load_data)

        time.sleep(5)  # 每5秒更新一次

if __name__ == "__main__":
    main()
