Name:		moshix
Version:	0.30.0
Release:	1
Summary:	Sealed class adapters for Moshi
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/ZacSweers/moshiX
# Tag 0.30.0 (98abd5ea5c6c4eb6840d0d56b23a341e819befc1).
# moshi-sealed runtime and reflect only. The upstream build is Gradle.
# This package compiles those sources with the installed kotlinc.
Source0:	moshix-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-21-openjdk-devel
BuildRequires:	kotlin = 2.0.21
BuildRequires:	kotlin-libs = 2.0.21
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(com.squareup.moshi:moshi) = 1.15.2
BuildRequires:	mvn(com.squareup.moshi:moshi-adapters) = 1.15.2
BuildRequires:	mvn(com.squareup.moshi:moshi-kotlin) = 1.15.2
BuildRequires:	mvn(com.squareup.okio:okio)
BuildRequires:	mvn(com.google.code.findbugs:jsr305)

%description
dev.zacsweers.moshix:moshi-sealed-runtime %{version}. Annotations and
helpers that Moshi uses to decode sealed classes.

%package sealed-reflect
Summary:	Reflective sealed-class JsonAdapter for Moshi
Group:		Development/Java
Requires:	moshix = %{EVRD}
Requires:	mvn(com.squareup.moshi:moshi-kotlin) = 1.15.2
Requires:	mvn(org.jetbrains.kotlin:kotlin-reflect)

%description sealed-reflect
dev.zacsweers.moshix:moshi-sealed-reflect %{version}.
MoshiSealedJsonAdapterFactory reads TypeLabel annotations through
kotlin-reflect.

%prep
%autosetup -n moshix-%{version}
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
test -s LICENSE.txt
test -s moshi-sealed/runtime/src/main/kotlin/dev/zacsweers/moshix/sealed/annotations/TypeLabel.kt
test -s moshi-sealed/reflect/src/main/kotlin/dev/zacsweers/moshix/sealed/reflect/MoshiSealedJsonAdapterFactory.kt
test -s check/SealedMsg.kt
test -s check/SealedCheck.java

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
CP="%{_javadir}/moshi.jar:%{_javadir}/moshi-adapters.jar:%{_javadir}/okio.jar:%{_javadir}/javax.annotation.jar:%{_javadir}/kotlin-stdlib.jar:%{_javadir}/kotlin-reflect.jar"
mkdir -p rtclasses
find moshi-sealed/runtime/src/main/kotlin -name '*.kt' > rt.src
test "$(wc -l < rt.src)" -eq 7
kotlinc -jvm-target 1.8 -language-version 2.0 -no-stdlib \
	-jdk-home "$JAVA_HOME" -J-Xmx2g \
	-cp "$CP" \
	-d rtclasses @rt.src
jar cf moshi-sealed-runtime.jar -C rtclasses .
jar i moshi-sealed-runtime.jar
mkdir -p rfclasses
find moshi-sealed/reflect/src/main/kotlin -name '*.kt' > rf.src
test "$(wc -l < rf.src)" -eq 1
kotlinc -jvm-target 1.8 -language-version 2.0 -no-stdlib \
	-jdk-home "$JAVA_HOME" -J-Xmx2g \
	-cp "moshi-sealed-runtime.jar:%{_javadir}/moshi-kotlin.jar:$CP" \
	-d rfclasses @rf.src
jar cf moshi-sealed-reflect.jar -C rfclasses .
jar i moshi-sealed-reflect.jar
test -s moshi-sealed-runtime.jar
test -s moshi-sealed-reflect.jar

cat > moshi-sealed-runtime.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>dev.zacsweers.moshix</groupId>
  <artifactId>moshi-sealed-runtime</artifactId>
  <version>%{version}</version>
  <name>Moshi sealed runtime</name>
  <description>Annotations for Moshi sealed-class adapters.</description>
  <url>https://github.com/ZacSweers/moshiX</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.squareup.moshi</groupId>
      <artifactId>moshi</artifactId>
      <version>1.15.2</version>
    </dependency>
    <dependency>
      <groupId>com.squareup.moshi</groupId>
      <artifactId>moshi-adapters</artifactId>
      <version>1.15.2</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-stdlib</artifactId>
      <version>2.0.21</version>
    </dependency>
  </dependencies>
</project>
END

cat > moshi-sealed-reflect.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>dev.zacsweers.moshix</groupId>
  <artifactId>moshi-sealed-reflect</artifactId>
  <version>%{version}</version>
  <name>Moshi sealed reflect</name>
  <description>Reflective JsonAdapter.Factory for Moshi sealed classes.</description>
  <url>https://github.com/ZacSweers/moshiX</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>dev.zacsweers.moshix</groupId>
      <artifactId>moshi-sealed-runtime</artifactId>
      <version>%{version}</version>
    </dependency>
    <dependency>
      <groupId>com.squareup.moshi</groupId>
      <artifactId>moshi</artifactId>
      <version>1.15.2</version>
    </dependency>
    <dependency>
      <groupId>com.squareup.moshi</groupId>
      <artifactId>moshi-adapters</artifactId>
      <version>1.15.2</version>
    </dependency>
    <dependency>
      <groupId>com.squareup.moshi</groupId>
      <artifactId>moshi-kotlin</artifactId>
      <version>1.15.2</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-reflect</artifactId>
      <version>2.0.21</version>
    </dependency>
  </dependencies>
</project>
END

%install
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
mkdir -p %{buildroot}
sysjar install --buildroot %{buildroot} \
	--artifact moshi-sealed-runtime.pom:moshi-sealed-runtime.jar \
	--file-name moshi-sealed-runtime \
	--filelist runtime.list
grep -F -q '%%dir /usr/share/sysjar/index/dev.zacsweers.moshix' runtime.list
sysjar install --buildroot %{buildroot} \
	--artifact moshi-sealed-reflect.pom:moshi-sealed-reflect.jar \
	--file-name moshi-sealed-reflect \
	--filelist reflect.list
grep -v -F '%%dir /usr/share/sysjar/index/dev.zacsweers.moshix' reflect.list > reflect.files
if grep -F -q '%%dir /usr/share/sysjar/index/dev.zacsweers.moshix' reflect.files; then
	exit 1
fi
/bin/cp runtime.list runtime.files

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
RT=%{buildroot}%{_javadir}/moshi-sealed-runtime.jar
RF=%{buildroot}%{_javadir}/moshi-sealed-reflect.jar
test -s "$RT"
test -s "$RF"
CP="$RT:$RF:%{_javadir}/moshi.jar:%{_javadir}/moshi-adapters.jar:%{_javadir}/moshi-kotlin.jar:%{_javadir}/okio.jar:%{_javadir}/javax.annotation.jar:%{_javadir}/kotlin-stdlib.jar:%{_javadir}/kotlin-reflect.jar"
mkdir -p check/out
kotlinc -jvm-target 1.8 -language-version 2.0 -no-stdlib \
	-jdk-home "$JAVA_HOME" \
	-cp "$CP" \
	-d check/out check/SealedMsg.kt
javac --release 8 -encoding UTF-8 -cp "check/out:$CP" -d check/out check/SealedCheck.java
java -cp "check/out:$CP" SealedCheck > check/out.txt
cat check/out.txt
grep -F -qx 'moshix_ok {"type":"text","body":"hi"}' check/out.txt

%files -f runtime.files
%license LICENSE.txt
%doc README.md

%files sealed-reflect -f reflect.files
