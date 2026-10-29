import cvss

threats = [
    {
        'id': 'T-01',
        'desc': 'BOLA/IDOR status booking di BookingController',
        'dread_score': 40,
        'dread_level': 'CRITICAL',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-02',
        'desc': 'DoS Reverb WebSocket test-latency tanpa auth',
        'dread_score': 40,
        'dread_level': 'CRITICAL',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-03',
        'desc': 'Midtrans Webhook Callback Spoofing',
        'dread_score': 39,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-04',
        'desc': 'DoS Geolocation query & massive 10MB upload',
        'dread_score': 38,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-05',
        'desc': 'Stored XSS pada ulasan review dan catatan booking',
        'dread_score': 37,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-06',
        'desc': 'Mass Assignment Privilege Escalation role=admin',
        'dread_score': 37,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-07',
        'desc': 'Unrestricted File Upload Polyglot/SVG',
        'dread_score': 34,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-08',
        'desc': 'Insecure Session Storage unencrypted session sniffing',
        'dread_score': 34,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N'
    },
    {
        'id': 'T-09',
        'desc': 'IDOR Hashids pada percakapan chat',
        'dread_score': 33,
        'dread_level': 'HIGH',
        'vector': 'CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N'
    }
]

print(f"{'ID':<5} | {'CVSS Vector':<66} | {'CVSS':<5} | {'CVSS Sev':<8} | {'DREAD':<5} | {'DREAD Sev':<9} | {'Status':<7}")
print('-'*118)
for t in threats:
    c = cvss.CVSS4(t['vector'])
    cvss_score = c.base_score
    cvss_sev = c.severity.upper()
    status = 'Sama' if cvss_sev == t['dread_level'] else 'Berbeda'
    print(f"{t['id']:<5} | {t['vector']:<66} | {cvss_score:<5} | {cvss_sev:<8} | {t['dread_score']:<5} | {t['dread_level']:<9} | {status:<7}")
