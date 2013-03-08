### Dependency
- apt-get install libxml2-dev libxslt-dev
- <https://github.com/openstack/oslo-incubator>
- <https://github.com/openstack/oslo-config.git>


### TODO:

1) Mapr 为每个用户开辟一个Project，需要过滤非用户建立的 Project. 需要为完成:

- 在Horizon下过滤非用户建立 Project 的auth。(context_processors, context['authorized_tenants'])
- 在Nova下限制非用户建立 Project 的 API 调用。 (prolicy.json)
