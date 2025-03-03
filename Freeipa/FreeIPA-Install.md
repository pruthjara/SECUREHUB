


sudo apt remove --purge freeipa-client -y
sudo rm -rf /etc/ipa /var/lib/ipa /var/log/ipa* /var/lib/sss /etc/krb5.conf /var/lib/krb5kdc
sudo apt remove --purge sssd* -y
sudo rm -rf /etc/sssd /var/lib/sss /var/log/sssd
