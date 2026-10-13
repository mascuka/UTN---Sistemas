/* Motor de Java para el navegador: carga el compilador (javac + TeaVM, compilado a WebAssembly GC).
   Este archivo es el código de arranque del compilador, tal cual lo distribuye WASM-OJ
   (@wasm-oj/server 0.2.4, src/compiler: java-compiler-runtime.mjs y java-compiler-bindings.mjs,
   que vienen de TeaVM, y java-gc.ts). Licencias: TeaVM, Apache-2.0; WASM-OJ, MIT. Ver LICENCIAS.md.
   Lo único que se usa desde afuera es cargarMotor(bytes): devuelve el motor con createCompiler(). */
//#region src/compiler/vendor/java-compiler-runtime.mjs
var exceptionFrameRegex = /.+:wasm-function\[[0-9]+]:0x([0-9a-f]+).*/;
var getGlobalName = function(name) {
	return name.split(".").reduce((object, key) => object[key], globalThis);
};
var setGlobalName = function(name, value) {
	const path = name.split(".");
	const key = path.pop();
	const object = path.reduce((object, key) => object[key], globalThis);
	object[key] = value;
};
function defaults(imports, userExports, options, module, stringBuiltins) {
	let context = {
		exports: null,
		userExports,
		stackDeobfuscator: null
	};
	if (!stringBuiltins) stringImports(imports);
	dateImports(imports);
	consoleImports(imports, context);
	coreImports(imports, context, options, module);
	asyncImports(imports, context);
	jsoImports(imports, context, stringBuiltins, options);
	imports.teavmMath = Math;
	return {
		supplyExports(exports) {
			context.exports = exports;
		},
		supplyStackDeobfuscator(deobfuscator) {
			context.stackDeobfuscator = deobfuscator;
		}
	};
}
var javaExceptionSymbol = Symbol("javaException");
var JavaError = class extends Error {
	#context;
	constructor(context, javaException) {
		super();
		this.#context = context;
		this[javaExceptionSymbol] = javaException;
		context.exports["teavm.setJsException"](javaException, this);
	}
	get message() {
		let exceptionMessage = this.#context.exports["teavm.exceptionMessage"];
		let stringToJs = this.#context.exports["teavm.stringToJs"];
		if (typeof exceptionMessage === "function" && typeof stringToJs === "function") {
			let message = exceptionMessage(this[javaExceptionSymbol]);
			if (message != null) return stringToJs(message);
		}
		return "(could not fetch message)";
	}
};
function stringImports(imports) {
	imports["wasm:js-string"] = {
		fromCharCode: (code) => String.fromCharCode(code),
		fromCharCodeArray: () => {
			throw new Error("Not supported");
		},
		intoCharCodeArray: () => {
			throw new Error("Not supported");
		},
		concat: (first, second) => first + second,
		charCodeAt: (string, index) => string.charCodeAt(index),
		length: (s) => s.length,
		substring: (s, start, end) => s.substring(start, end)
	};
}
function dateImports(imports) {
	imports.teavmDate = {
		currentTimeMillis: () => (/* @__PURE__ */ new Date()).getTime(),
		dateToString: (timestamp) => new Date(timestamp).toString(),
		getYear: (timestamp) => new Date(timestamp).getFullYear(),
		setYear(timestamp, year) {
			let date = new Date(timestamp);
			date.setFullYear(year);
			return date.getTime();
		},
		getMonth: (timestamp) => new Date(timestamp).getMonth(),
		setMonth(timestamp, month) {
			let date = new Date(timestamp);
			date.setMonth(month);
			return date.getTime();
		},
		getDate: (timestamp) => new Date(timestamp).getDate(),
		setDate(timestamp, value) {
			let date = new Date(timestamp);
			date.setDate(value);
			return date.getTime();
		},
		create: (year, month, date, hrs, min, sec) => new Date(year, month, date, hrs, min, sec).getTime(),
		createFromUTC: (year, month, date, hrs, min, sec) => Date.UTC(year, month, date, hrs, min, sec)
	};
}
function consoleImports(imports) {
	let stderr = "";
	let stdout = "";
	imports.teavmConsole = {
		putcharStderr(c) {
			if (c === 10) {
				console.error(stderr);
				stderr = "";
			} else stderr += String.fromCharCode(c);
		},
		putcharStdout(c) {
			if (c === 10) {
				console.log(stdout);
				stdout = "";
			} else stdout += String.fromCharCode(c);
		}
	};
}
function coreImports(imports, context, options, module) {
	let memoryOptions = options.memory || {};
	let finalizationRegistry = new FinalizationRegistry((heldValue) => {
		let report = context.exports["teavm.reportGarbageCollectedValue"];
		if (typeof report !== "undefined") report(heldValue.queue, heldValue.ref);
	});
	let stringFinalizationRegistry = new FinalizationRegistry((heldValue) => {
		let report = context.exports["teavm.reportGarbageCollectedString"];
		if (typeof report === "function") report(heldValue);
	});
	imports.teavm = {
		createWeakRef(value, ref, queue) {
			if (queue !== null) finalizationRegistry.register(value, {
				ref,
				queue
			});
			return new WeakRef(value);
		},
		deref: (weakRef) => {
			let result = weakRef.deref();
			return result !== void 0 ? result : null;
		},
		createStringWeakRef(value, heldValue) {
			stringFinalizationRegistry.register(value, heldValue);
			return new WeakRef(value);
		},
		stringDeref: (weakRef) => weakRef.deref(),
		takeStackTrace() {
			let stack = (/* @__PURE__ */ new Error()).stack;
			let addresses = [];
			for (let line of stack.split("\n")) {
				let match = exceptionFrameRegex.exec(line);
				if (match !== null && match.length >= 2) {
					let address = parseInt(match[1], 16);
					addresses.push(address);
				}
			}
			return { getStack() {
				let result;
				if (context.stackDeobfuscator) try {
					result = context.stackDeobfuscator(addresses);
				} catch (e) {
					console.warn("Could not deobfuscate stack", e);
				}
				if (!result) result = addresses.map((address) => {
					return {
						className: "java.lang.Throwable$FakeClass",
						method: "fakeMethod",
						file: "Throwable.java",
						line: address
					};
				});
				return result;
			} };
		},
		decorateException(javaException) {
			new JavaError(context, javaException);
		},
		linearMemory() {
			return context.exports["teavm.memory"].buffer;
		},
		notifyHeapResized: memoryOptions.onResize || function() {}
	};
	if (module) {
		let memDefaults = getMemoryDefaults(module);
		if (memDefaults !== null ? memDefaults.imported : hasImportedMemory(module)) {
			let memoryInstance = memoryOptions["external"];
			if (!memoryInstance) {
				if (memDefaults === null) memDefaults = {};
				let minSize = memoryOptions.minSize || memDefaults.min || 0;
				let maxSize = memoryOptions.maxSize || memDefaults.max;
				memoryInstance = new WebAssembly.Memory({
					shared: memoryOptions.shared === true,
					initial: minSize,
					maximum: maxSize
				});
			}
			imports.teavm.memory = memoryInstance;
		}
	}
}
function asyncImports(imports) {
	imports.teavmAsync = {
		offer(instance, fn, time) {
			let dt = Math.max(0, time - Date.now());
			return setTimeout(() => {
				fn(instance);
			}, dt);
		},
		kill(id) {
			clearTimeout(id);
		}
	};
}
function hasImportedMemory(module) {
	return WebAssembly.Module.imports(module).findIndex(({ module, name, kind }) => module === "teavm" && name === "memory" && kind === "memory") >= 0;
}
function getMemoryDefaults(module) {
	let sections = WebAssembly.Module.customSections(module, "teavm.memoryRequirements");
	if (sections.length !== 1) return null;
	return JSON.parse(new TextDecoder().decode(sections[0]));
}
function jsoImports(imports, context, stringBuiltins, options) {
	let javaObjectSymbol = Symbol("javaObject");
	let functionsSymbol = Symbol("functions");
	let functionOriginSymbol = Symbol("functionOrigin");
	let wrapperCallMarkerSymbol = Symbol("wrapperCallMarker");
	let jsWrappers = /* @__PURE__ */ new WeakMap();
	let javaWrappers = /* @__PURE__ */ new WeakMap();
	let primitiveWrappers = /* @__PURE__ */ new Map();
	let primitiveFinalization = new FinalizationRegistry((token) => primitiveWrappers.delete(token));
	let hashCodes = /* @__PURE__ */ new WeakMap();
	let lastHashCode = 2463534242;
	let nextHashCode = () => {
		let x = lastHashCode;
		x ^= x << 13;
		x ^= x >>> 17;
		x ^= x << 5;
		lastHashCode = x;
		return x;
	};
	function identity(value) {
		return value;
	}
	function sanitizeName(str) {
		let result = "";
		let firstChar = str.charAt(0);
		result += isIdentifierStart(firstChar) ? firstChar : "_";
		for (let i = 1; i < str.length; ++i) {
			let c = str.charAt(i);
			result += isIdentifierPart(c) ? c : "_";
		}
		return result;
	}
	function isIdentifierStart(s) {
		return s >= "A" && s <= "Z" || s >= "a" && s <= "z" || s === "_" || s === "$";
	}
	function isIdentifierPart(s) {
		return isIdentifierStart(s) || s >= "0" && s <= "9";
	}
	function setProperty(obj, prop, value) {
		if (obj === null) setGlobalName(prop, value);
		else obj[prop] = value;
	}
	function javaExceptionToJs(e) {
		if (e instanceof WebAssembly.Exception) {
			let tag = context.exports["teavm.javaException"];
			let getJsException = context.exports["teavm.getJsException"];
			if (e.is(tag)) {
				let javaException = e.getArg(tag, 0);
				let extracted = extractException(javaException);
				if (extracted !== null) return extracted;
				let wrapper = getJsException(javaException);
				if (typeof wrapper === "undefined") wrapper = new JavaError(context, javaException);
				return wrapper;
			}
		}
		return e;
	}
	function jsExceptionAsJava(e) {
		if (javaExceptionSymbol in e) return e[javaExceptionSymbol];
		else return context.exports["teavm.js.wrapException"](e);
	}
	function rethrowJsAsJava(e) {
		context.exports["teavm.js.throwException"](jsExceptionAsJava(e));
	}
	function extractException(e) {
		return context.exports["teavm.js.extractException"](e);
	}
	function rethrowJavaAsJs(e) {
		throw javaExceptionToJs(e);
	}
	function getProperty(obj, prop) {
		try {
			return obj !== null ? obj[prop] : getGlobalName(prop);
		} catch (e) {
			rethrowJsAsJava(e);
		}
	}
	function defineFunction(fn, vararg) {
		const count = fn.length - (vararg ? 1 : 0);
		const wrapper = function(...args) {
			try {
				return vararg ? fn(...Array.from({ length: count }, (_, index) => args[index]), args.slice(count)) : fn(...Array.from({ length: count }, (_, index) => args[index]));
			} catch (e) {
				rethrowJavaAsJs(e);
			}
		};
		Object.defineProperty(wrapper, "length", { value: count });
		return wrapper;
	}
	function renameConstructor(name, constructor) {
		return { [name]: function(marker, javaObject) {
			return constructor.call(this, marker, javaObject);
		} }[name];
	}
	imports.teavmJso = {
		stringBuiltinsSupported: () => stringBuiltins,
		isUndefined: (o) => typeof o === "undefined",
		emptyArray: () => [],
		appendToArray: (array, e) => array.push(e),
		unwrapBoolean: (value) => value ? 1 : 0,
		wrapBoolean: (value) => !!value,
		getProperty,
		setProperty,
		setPropertyPure: setProperty,
		global(name) {
			try {
				return getGlobalName(name);
			} catch (e) {
				rethrowJsAsJava(e);
			}
		},
		createClass(name, parent, constructor) {
			name = sanitizeName(name || "JavaObject");
			let action;
			let fn = renameConstructor(name, function(marker, javaObject) {
				if (marker === wrapperCallMarkerSymbol) action.call(this, javaObject);
				else if (constructor === null) throw new Error("This class can't be instantiated directly");
				else try {
					return constructor.apply(null, arguments);
				} catch (e) {
					rethrowJavaAsJs(e);
				}
			});
			if (parent === null) action = function(javaObject) {
				this[javaObjectSymbol] = javaObject;
				this[functionsSymbol] = null;
			};
			else action = function(javaObject) {
				parent.call(this, javaObject);
			};
			fn.prototype = Object.create(parent ? parent.prototype : Object.prototype);
			fn.prototype.constructor = fn;
			let boundFn = renameConstructor(name, function(javaObject) {
				return fn.call(this, wrapperCallMarkerSymbol, javaObject);
			});
			boundFn[wrapperCallMarkerSymbol] = fn;
			boundFn.prototype = fn.prototype;
			return boundFn;
		},
		exportClass(cls) {
			return cls[wrapperCallMarkerSymbol];
		},
		defineMethod(cls, name, fn, vararg) {
			const method = defineFunction(fn, vararg);
			cls.prototype[name] = function(...args) {
				return method(this, ...args);
			};
			Object.defineProperty(cls.prototype[name], "length", { value: method.length - 1 });
		},
		defineStaticMethod(cls, name, fn, vararg) {
			cls[name] = defineFunction(fn, vararg);
		},
		defineFunction,
		defineProperty(cls, name, getFn, setFn) {
			let descriptor = { get() {
				try {
					return getFn(this);
				} catch (e) {
					rethrowJavaAsJs(e);
				}
			} };
			if (setFn !== null) descriptor.set = function(value) {
				try {
					setFn(this, value);
				} catch (e) {
					rethrowJavaAsJs(e);
				}
			};
			Object.defineProperty(cls.prototype, name, descriptor);
		},
		defineStaticProperty(cls, name, getFn, setFn) {
			let descriptor = { get() {
				try {
					return getFn();
				} catch (e) {
					rethrowJavaAsJs(e);
				}
			} };
			if (setFn !== null) descriptor.set = function(value) {
				try {
					setFn(value);
				} catch (e) {
					rethrowJavaAsJs(e);
				}
			};
			Object.defineProperty(cls, name, descriptor);
		},
		javaObjectToJS(instance, cls) {
			if (instance === null) return null;
			let existing = jsWrappers.get(instance);
			if (typeof existing != "undefined") {
				let result = existing.deref();
				if (typeof result !== "undefined") return result;
			}
			let obj = new cls(instance);
			jsWrappers.set(instance, new WeakRef(obj));
			return obj;
		},
		unwrapJavaObject(instance) {
			return instance[javaObjectSymbol];
		},
		asFunction(instance, propertyName) {
			if (instance === null || instance === void 0) return null;
			let functions = instance[functionsSymbol];
			if (functions === null) {
				functions = Object.create(null);
				instance[functionsSymbol] = functions;
			}
			let result = functions[propertyName];
			if (typeof result !== "function") {
				result = function() {
					return instance[propertyName].apply(instance, arguments);
				};
				result[functionOriginSymbol] = instance;
				functions[propertyName] = result;
			}
			return result;
		},
		functionAsObject(fn, property) {
			if (fn === null || fn === void 0) return null;
			let origin = fn[functionOriginSymbol];
			if (typeof origin !== "undefined") {
				let functions = origin[functionsSymbol];
				if (functions !== void 0 && functions[property] === fn) return origin;
			}
			return { [property]: function(...args) {
				try {
					return fn(...args);
				} catch (e) {
					rethrowJavaAsJs(e);
				}
			} };
		},
		wrapObject(obj) {
			if (obj === null) return null;
			if (typeof obj === "object" || typeof obj === "function" || false) {
				let result = obj[javaObjectSymbol];
				if (typeof result === "object") return result;
				result = javaWrappers.get(obj);
				if (result !== void 0) {
					result = result.deref();
					if (result !== void 0) return result;
				}
				result = context.exports["teavm.jso.createWrapper"](obj);
				javaWrappers.set(obj, new WeakRef(result));
				return result;
			} else {
				let result = primitiveWrappers.get(obj);
				if (result !== void 0) {
					result = result.deref();
					if (result !== void 0) return result;
				}
				result = context.exports["teavm.jso.createWrapper"](obj);
				primitiveWrappers.set(obj, new WeakRef(result));
				primitiveFinalization.register(result, obj);
				return result;
			}
		},
		isPrimitive: (value, type) => typeof value === type || value === null,
		instanceOf: (value, type) => value instanceof type,
		instanceOfOrNull: (value, type) => value === null || value instanceof type,
		sameRef: (a, b) => a === b,
		hashCode: (obj) => {
			if (typeof obj === "object" || typeof obj === "function" || typeof obj === "symbol") {
				let code = hashCodes.get(obj);
				if (typeof code === "number") return code;
				code = nextHashCode();
				hashCodes.set(obj, code);
				return code;
			} else if (typeof obj === "number") return obj | 0;
			else if (typeof obj === "bigint") return BigInt.asIntN(obj, 32);
			else if (typeof obj === "boolean") return obj ? 1 : 0;
			else return 0;
		},
		apply: (instance, method, args) => {
			try {
				if (instance === null) return getGlobalName(method)(...args);
				else return instance[method](...args);
			} catch (e) {
				rethrowJsAsJava(e);
			}
		},
		concatArray: (a, b) => [...a, ...b],
		getJavaException: (e) => e[javaExceptionSymbol],
		getJSException: (e) => {
			let getJsException = context.exports["teavm.getJsException"];
			return getJsException(e);
		},
		jsExports: () => context.userExports
	};
	for (let name of [
		"wrapByte",
		"wrapShort",
		"wrapChar",
		"wrapInt",
		"wrapLong",
		"wrapFloat",
		"wrapDouble",
		"unwrapByte",
		"unwrapShort",
		"unwrapChar",
		"unwrapInt",
		"unwrapLong",
		"unwrapFloat",
		"unwrapDouble"
	]) imports.teavmJso[name] = identity;
	function wrapCallFromJavaToJs(call) {
		try {
			return call();
		} catch (e) {
			rethrowJsAsJava(e);
		}
	}
	for (let i = 0; i < 32; ++i) {
		imports.teavmJso["createFunction" + i] = function(...parts) {
			const factory = options.jsBodyFactories?.get(JSON.stringify(parts));
			if (!factory) throw new Error("Missing statically compiled TeaVM JavaScript body");
			return factory.bind(this, wrapCallFromJavaToJs);
		};
		imports.teavmJso["bindFunction" + i] = (f, ...args) => f.bind(null, ...args);
		imports.teavmJso["callFunction" + i] = (fn, ...args) => {
			try {
				return fn(...args);
			} catch (e) {
				rethrowJsAsJava(e);
			}
		};
		imports.teavmJso["callMethod" + i] = (instance, method, ...args) => {
			try {
				return instance !== null ? instance[method](...args) : getGlobalName(method)(...args);
			} catch (e) {
				rethrowJsAsJava(e);
			}
		};
		imports.teavmJso["construct" + i] = (constructor, ...args) => {
			try {
				return Reflect.construct(constructor, args);
			} catch (e) {
				rethrowJsAsJava(e);
			}
		};
		imports.teavmJso["arrayOf" + i] = (...args) => args;
	}
}
var hasStringBuiltinsPromise = null;
function hasStringBuiltins() {
	if (hasStringBuiltinsPromise === null) hasStringBuiltinsPromise = (async () => {
		let bytes = new Int8Array([
			0,
			97,
			115,
			109,
			1,
			0,
			0,
			0,
			1,
			7,
			1,
			96,
			1,
			127,
			1,
			100,
			111,
			2,
			31,
			1,
			14,
			119,
			97,
			115,
			109,
			58,
			106,
			115,
			45,
			115,
			116,
			114,
			105,
			110,
			103,
			12,
			102,
			114,
			111,
			109,
			67,
			104,
			97,
			114,
			67,
			111,
			100,
			101,
			0,
			0,
			3,
			1,
			0,
			5,
			4,
			1,
			1,
			0,
			0,
			7,
			10,
			1,
			6,
			109,
			101,
			109,
			111,
			114,
			121,
			2,
			0,
			10,
			-127,
			-128,
			-128,
			0,
			0
		]);
		try {
			let response = new Response(bytes, { headers: { "Content-Type": "application/wasm" } });
			let module = await WebAssembly.compileStreaming(response, { builtins: ["js-string"] });
			await WebAssembly.instantiate(module, {}, { builtins: ["js-string"] });
			return true;
		} catch (e) {
			return false;
		}
	})();
	return hasStringBuiltinsPromise;
}
var compileJavaModule = (bytes) => WebAssembly.compile(bytes, { builtins: ["js-string"] });
//#endregion
//#region src/compiler/vendor/java-compiler-bindings.mjs
var jsBodyFactories = /* @__PURE__ */ new Map([
	["[\"return Object.create(null);\"]", function(wrapCallFromJavaToJs) {
		return Object.create(null);
	}],
	["[\"array\",\"return array;\"]", function(wrapCallFromJavaToJs, array) {
		return array;
	}],
	["[\"str\",\"return str;\"]", function(wrapCallFromJavaToJs, str) {
		return str;
	}],
	["[\"__this__\",\"return __this__;\"]", function(wrapCallFromJavaToJs, __this__) {
		return __this__;
	}],
	["[\"number\",\"return number;\"]", function(wrapCallFromJavaToJs, number) {
		return number;
	}],
	["[\"str\",\"return str;\"]", function(wrapCallFromJavaToJs, str) {
		return str;
	}],
	["[\"size\",\"return new Array(size);\"]", function(wrapCallFromJavaToJs, size) {
		return new Array(size);
	}]
]);
//#endregion
//#region src/compiler/java-gc.ts
async function loadJavaGcEngine(bytes) {
	const wasmModule = await compileJavaModule(bytes);
	const imports = {};
	const exports = {};
	const context = defaults(imports, exports, { jsBodyFactories }, wasmModule, await hasStringBuiltins());
	const instance = await WebAssembly.instantiate(wasmModule, imports);
	context.supplyExports(instance.exports);
	for (const [key, value] of Object.entries(instance.exports)) if (value instanceof WebAssembly.Global) Object.defineProperty(exports, key, { get: () => value.value });
	if (typeof exports.createCompiler !== "function") throw new Error("The pinned Java compiler has no createCompiler export.");
	return exports;
}

export const cargarMotor = loadJavaGcEngine;
