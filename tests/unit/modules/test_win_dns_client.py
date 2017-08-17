# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Jayesh Kariya <jayeshk@saltstack.com>`
'''

# Import Python Libs
from __future__ import absolute_import
import types

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import (
    MagicMock,
    patch,
    Mock,
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
import salt.modules.win_dns_client as win_dns_client


class Mockwmi(object):
    '''
    Mock wmi class
    '''
    NetConnectionID = 'Local Area Connection'
    Index = 0
    DNSServerSearchOrder = ['10.1.1.10']
    Description = 'Local Area Connection'
    DHCPEnabled = True

    def __init__(self):
        pass


class Mockwinapi(object):
    '''
    Mock winapi class
    '''
    def __init__(self):
        pass

    class winapi(object):
        '''
        Mock winapi class
        '''
        def __init__(self):
            pass

        @staticmethod
        def Com():
            '''
            Mock Com method
            '''
            return True


@skipIf(NO_MOCK, NO_MOCK_REASON)
class WinDnsClientTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.modules.win_dns_client
    '''

    def setup_loader_modules(self):
        # wmi and pythoncom modules are platform specific...
        wmi = types.ModuleType('wmi')
        pythoncom = types.ModuleType('pythoncom')
        sys_modules_patcher = patch.dict('sys.modules', {'wmi': wmi, 'pythoncom': pythoncom})
        sys_modules_patcher.start()
        self.addCleanup(sys_modules_patcher.stop)
        self.WMI = Mock()
        self.addCleanup(delattr, self, 'WMI')
        wmi.WMI = Mock(return_value=self.WMI)
        pythoncom.CoInitialize = Mock()
        pythoncom.CoUninitialize = Mock()
        return {win_dns_client: {'wmi': wmi}}

    # 'get_dns_servers' function tests: 1

    def test_get_dns_servers(self):
        '''
        Test if it return a list of the configured DNS servers
        of the specified interface.
        '''
        with patch('salt.utils', Mockwinapi), \
                patch('salt.utils.winapi.Com', MagicMock()), \
                patch.object(self.WMI, 'Win32_NetworkAdapter',
                             return_value=[Mockwmi()]), \
                patch.object(self.WMI, 'Win32_NetworkAdapterConfiguration',
                             return_value=[Mockwmi()]):
            self.assertListEqual(win_dns_client.get_dns_servers
                                 ('Local Area Connection'),
                                 ['10.1.1.10'])

            self.assertFalse(win_dns_client.get_dns_servers('Ethernet'))

    # 'rm_dns' function tests: 1

    def test_rm_dns(self):
        '''
        Test if it remove the DNS server from the network interface.
        '''
        with patch.dict(win_dns_client.__salt__,
                        {'cmd.retcode': MagicMock(return_value=0)}):
            self.assertTrue(win_dns_client.rm_dns('10.1.1.10'))

    # 'add_dns' function tests: 1

    def test_add_dns(self):
        '''
        Test if it add the DNS server to the network interface.
        '''
        with patch('salt.utils.winapi.Com', MagicMock()):
            with patch.object(self.WMI, 'Win32_NetworkAdapter',
                              return_value=[Mockwmi()]):
                with patch.object(self.WMI, 'Win32_NetworkAdapterConfiguration',
                                  return_value=[Mockwmi()]):
                    self.assertFalse(win_dns_client.add_dns('10.1.1.10',
                                                            'Ethernet'))

                    self.assertTrue(win_dns_client.add_dns
                                    ('10.1.1.10', 'Local Area Connection'))

        with patch.object(win_dns_client, 'get_dns_servers',
                          MagicMock(return_value=['10.1.1.10'])):
            with patch.dict(win_dns_client.__salt__,
                            {'cmd.retcode': MagicMock(return_value=0)}):
                self.assertTrue(win_dns_client.add_dns('10.1.1.0',
                                                       'Local Area Connection'))

    # 'dns_dhcp' function tests: 1

    def test_dns_dhcp(self):
        '''
        Test if it configure the interface to get its
        DNS servers from the DHCP server
        '''
        with patch.dict(win_dns_client.__salt__,
                        {'cmd.retcode': MagicMock(return_value=0)}):
            self.assertTrue(win_dns_client.dns_dhcp())

    # 'get_dns_config' function tests: 1

    def test_get_dns_config(self):
        '''
        Test if it get the type of DNS configuration (dhcp / static)
        '''
        with patch('salt.utils.winapi.Com', MagicMock()):
            with patch.object(self.WMI, 'Win32_NetworkAdapter',
                              return_value=[Mockwmi()]):
                with patch.object(self.WMI, 'Win32_NetworkAdapterConfiguration',
                                  return_value=[Mockwmi()]):
                    self.assertTrue(win_dns_client.get_dns_config())