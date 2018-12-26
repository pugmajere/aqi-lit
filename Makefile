build:
	/bin/true

LIB = /usr/lib/aqi-lit/

BIN_TARGETS = $(patsubst src/%.py,$(DESTDIR)/$(LIB)/%.py, $(wildcard src/*.py))

$(DESTDIR)/$(LIB)/%.py: src/%.py
	mkdir -p $(DESTDIR)/$(LIB)
	cp $< $@


install: $(BIN_TARGETS) $(SYSTEMD) $(PERL_LIB_TARGETS)
	mkdir -p $(DESTDIR)/lib/systemd/system/
	cp systemd/aqi-lit.service $(DESTDIR)/lib/systemd/system/
