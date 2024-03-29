"""Generating CloudFormation template.""" 
 
from troposphere import ( 
    Base64, 
    ec2, 
    GetAtt, 
    Join, 
    Output, 
    Parameter, 
    Ref, 
    Template, 
) 

from ipaddress import ip_network

from ipify import get_ip

ApplicationPort = "3000" 

PublicCidrIp = str(ip_network(get_ip()))

t = Template() 

t.add_description("Effective DevOps in AWS: HelloWorld web application") 

t.add_parameter(Parameter( 
    "KeyPair", 
    Description="Name of an existing EC2 KeyPair to SSH", 
    Type="AWS::EC2::KeyPair::KeyName", 
    ConstraintDescription="must be the name of an existing EC2 KeyPair.", 
))

t.add_resource(ec2.SecurityGroup( 
    "SecurityGroup", 
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort), 
    SecurityGroupIngress=[ 
        ec2.SecurityGroupRule( 
            IpProtocol="tcp", 
            FromPort="22", 
            ToPort="22", 
            CidrIp=PublicCidrIp, 
        ), 
        ec2.SecurityGroupRule( 
            IpProtocol="tcp", 
            FromPort=ApplicationPort, 
            ToPort=ApplicationPort, 
            CidrIp="0.0.0.0/0", 
        ), 
    ], 
))

ud = Base64(Join('\n', [ 
    "#!/bin/bash", 
    "sudo yum install --enablerepo=epel -y nodejs", 
    "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js", 
    "wget http://bit.ly/2vVvT18 -O /etc/init/helloworld.conf", 
    "start helloworld" 
])) 

instance = ec2.Instance("myinstance")
instance.ImageId ="ami-51809835"
instance.InstanceType ="t2.micro"
instance.SecurityGroups=[Ref("SecurityGroup")]
instance.UserData = ud
instance.KeyName=Ref("KeyPair")

t.add_resource(instance)

t.add_output(Output( 
    "InstancePublicIp", 
    Description="Public IP of our instance.", 
    Value=GetAtt(instance, "PublicIp"), 
)) 
 
t.add_output(Output( 
    "WebUrl", 
    Description="Application endpoint", 
    Value=Join("", [ 
        "http://", GetAtt(instance, "PublicDnsName"), 
        ":", ApplicationPort 
    ]), 
)) 

print(t.to_json())
