# Introduction #
There was an issue that including jQuery will cause javascript error.

The error is document.body is null while running jQuery script. And this is caused by the relocation in [templates/loginProxy.html](http://code.google.com/p/flow-platform/source/browse/trunk/flow1.0/src/flow-site/templates/loginProxy.html)
```
<script type="text/javascript">
     location.href = '{{ redirectURI }}';
</script> 
```

The solution is simple. If this line is to be executed, don't include jQuery.