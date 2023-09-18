# Use dynlist overlay instead of deprecated memberOf

- status: accepted
- date: 2023-08-17
- deciders: IAM
- consulted: IAM
- informed: tech-intern

---

## Context and Problem Statement

Currently we use the `memberOf` overlay to generate the `memberOf` attribute
for user objects. This overlay is deprecated upstream. While still available
in UCS 5.2 we need a replacement mid-term or maintain it ourselves.

## Decision Drivers

- `memberOf` deprecated upstream
- no nested groups in `memberOf` attributes of `memberOf` overlay

## Considered Options

1. `dynlist` overlay module
1. keep `memberOf`

## Decision Outcome

Chosen option: "keep `memberOf`", because performance of `dynlist` in
unacceptable ATM.

### dynlist overlay as replacement for memberOf

The first test (primary UCS 5.2) looked promising, `memberOf` attribute even for nested groups are created by the `dynlist` module:

#### slapd.conf configuration

```text
overlay dynlist
dynlist-attrset groupOfURLs memberURL uniqueMember+memberOf@univentionGroup*

#moduleload              memberof.so
#overlay                 memberof
#memberof-group-oc       posixGroup
#memberof-member-ad      uniqueMember
#memberof-memberof-ad    memberOf
#memberof-dangling       ignore
#memberof-refint         false
```

#### LDAP objects

```text
dn: uid=test2,cn=users,dc=ucs,dc=test
  
dn: cn=basegroup,cn=groups,dc=ucs,dc=test
uniqueMember: uid=test1,cn=users,dc=ucs,dc=test
uniqueMember: uid=test2,cn=users,dc=ucs,dc=test

dn: cn=nested1,cn=groups,dc=ucs,dc=test
uniqueMember: cn=basegroup,cn=groups,dc=ucs,dc=test
```

#### ldapsearch one user object with memberOf

```text
univention-ldapsearch uid=test2 memberOf

dn: uid=test2,cn=users,dc=ucs,dc=test
memberOf: cn=basegroup,cn=groups,dc=ucs,dc=test
memberOf: cn=nested1,cn=groups,dc=ucs,dc=test
memberOf: cn=domain users,cn=groups,dc=ucs,dc=test
```

But the performance is a killer ATM. We created a test server with the test/utils/200.000-users.py tool from our performance test setup.

#### with `dynlist` module

```text
$ time univention-ldapsearch uid=testuser548 memberOf
...
real    0m21,885s
user    0m0,176s
sys     0m0,067s
```

#### with `memberOf` module

```shell
$ time univention-ldapsearch uid=testuser548 memberOf
...
real    0m0,248s
user    0m0,176s
sys     0m0,033
```

Even without "nested" groups feature (`dynlist-attrset groupOfURLs memberURL uniqueMember+memberOf@univentionGroup`, so without the `*`) it is a little bit faster, but still far from acceptable.

```shell
$ time univention-ldapsearch uid=testuser548 memberOf
...
real    0m12,797s
user    0m0,186s
sys     0m0,032s
```

## keep `memberOf`

Nothing to do, `memberOf` is still available and works in UCS 5.2.

## More Information

- https://www.kania-online.de/overlay-memberof-hat-den-status-deprecated-in-openldap-2-6/
- https://man7.org/linux/man-pages/man5/slapo-dynlist.5.html
- https://blog.oddbit.com/post/2013-07-22-generating-a-membero/
