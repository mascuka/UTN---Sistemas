package org.teavm.interop;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/** Solo para compilar las ayudas (Salida usa @Import): en el classlib de TeaVM ya está la verdadera. */
@Retention(RetentionPolicy.RUNTIME)
@Target({ ElementType.METHOD, ElementType.CONSTRUCTOR })
public @interface Import {
    String name();
    String module() default "";
}
